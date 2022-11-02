import os
import logging
from tempfile import TemporaryFile

import cv2
from PIL import Image

import tator
import inference


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Read environment variables that are provided from TATOR
host = os.getenv('HOST')
token = os.getenv('TOKEN')
project_id = int(os.getenv('PROJECT_ID'))
media_ids = [int(id_) for id_ in os.getenv('MEDIA_IDS').split(',')]
frames_per_inference = int(os.getenv('FRAMES_PER_INFERENCE', 30))

# Set up the TATOR API.
api = tator.get_api(host, token)

# Iterate through each video.
for media_id in media_ids:

    # Download video.
    media = api.get_media(media_id)
    logger.info(f"Downloading {media.name}...")
    out_path = f"/tmp/{media.name}"
    for progress in tator.util.download_media(api, media, out_path):
        logger.info(f"Download progress: {progress}%")

    # Do inference on each video.
    logger.info(f"Doing inference on {media.name}...")
    localizations = []
    vid = cv2.VideoCapture(out_path)
    frame_number = 0

    # Read *every* frame from the video, break when at the end.
    while True:
        ret, frame = vid.read()
        if not ret:
            break

        # Create a temporary file, access the image data, save data to file.
        framefile = TemporaryFile(suffix='.jpg')
        im = Image.fromarray(frame)
        im.save(framefile)

        # For every N frames, make a prediction; append prediction results
        # to a list, increase the frame count.
        if frame_number % frames_per_inference == 0:

            spec = {}

            # Predictions contains all information inside pandas dataframe
            predictions = inference.run_inference(framefile)

            for i, r in predictions.pandas().xyxy[0].iterrows:

                spec['media_id'] = media_id
                spec['type'] = None # Unsure, docs not specific
                spec['frame'] = frame_number

                x, y, x2, y2 = r['xmin'], r['ymin'], r['xmax'], r['ymax']
                w, h = x2 - x, y2 - y

                spec['x'] = x
                spec['y'] = y
                spec['width'] = w
                spec['height'] = h
                spec['class_category'] = r['name']
                spec['confidence'] = r['confidence']

                localizations.append(spec)

        frame_number += 1

    # End interaction with video properly.
    vid.release()

    logger.info(f"Uploading object detections on {media.name}...")

    # Create the localizations in the video.
    num_created = 0
    for response in tator.util.chunked_create(api.create_localization_list,
                                              project_id,
                                              localization_spec=localizations):
        num_created += len(response.id)

    # Output pretty logging information.
    logger.info(f"Successfully created {num_created} localizations on "
                f"{media.name}!")

    logger.info("-------------------------------------------------")

logger.info(f"Completed inference on {len(media_ids)} files.")