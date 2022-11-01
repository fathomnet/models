import os
import glob

import keras
from keras.preprocessing.image import ImageDataGenerator
from keras_retinanet.preprocessing.csv_generator import CSVGenerator
from keras_retinanet.models.resnet import custom_objects

import cv2
import numpy as np
from PIL import Image


def run_inference(image_path, threshold=0.125):
    """Function to run inference on a single image, but still uses the CSV
    generator to stay consistent with the original implementation. The only
    thing that changed is how predictions are extracted: this function
    follows the example notebook provided by the repo, and results appear to
    line up. Output is a list of dicts containing information on the
    predictions (for TATOR), and a PIL image for Gradio demo."""

    # If exists (from previously), delete it
    if os.path.exists(image_list):
        os.remove(image_list)

    # Create a new temp csv file to hold the image
    with open(image_list, 'w') as f:
        f.write(image_path + ",,,,,")

    test_image_data_generator = ImageDataGenerator()
    test_generator = CSVGenerator(image_list,
                                  class_file,
                                  None,
                                  test_image_data_generator,
                                  image_min_side=1100,
                                  image_max_side=1650,
                                  num_channels=3)

    # start collecting predictions
    predictions = []

    # Loads up the one and only image
    image = test_generator.load_image(0)

    # Creating a copy in RGB format for the Gradio demo
    out_image = image.copy()
    out_image = cv2.cvtColor(out_image, cv2.COLOR_BGR2RGB)

    image = test_generator.preprocess_image(image)
    image, scale = test_generator.resize_image(image)

    # run network
    _, _, detects = model.predict_on_batch(np.expand_dims(image, axis=0))

    # compute predicted labels and scores
    predicted_labels = np.argmax(detects[0, :, 4:], axis=1)
    scores = detects[0, np.arange(detects.shape[1]), 4 + predicted_labels]

    # correct for image scale
    detects[0, :, :4] /= scale

    # visualize detections
    for idx, (label, score) in enumerate(zip(predicted_labels, scores)):

        # Confidence Threshold
        if score < threshold:
            continue

        # Grabbing the bounding boxes
        b = detects[0, idx, :4].astype(int)
        x, y, x2, y2 = b
        w, h = x2 - x, y2 - y

        # Output for TATOR
        image_result = {'image_id': image_path,
                        'category_id': label,
                        'score': score,
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h}

        # Output PIL image for gradio demo:
        # Creating a rectangle, text; adding to drawing
        bbox_colors = (np.random.randint(0, 255),
                       np.random.randint(0, 255),
                       np.random.randint(0, 255))

        cv2.rectangle(out_image, (x, y), (x2, y2), bbox_colors, 3)
        caption = "{} {:.3f}".format(test_generator.label_to_name(label),
                                     score)
        cv2.putText(out_image,
                    caption,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_PLAIN,
                    1.5, (0, 0, 0), 3)

        cv2.putText(out_image,
                    caption,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_PLAIN,
                    1.5, (255, 255, 255), 2)

        predictions.append(image_result)

    return predictions, Image.fromarray(out_image)


# -----------------------------------------------------------------------------
# Configs
# -----------------------------------------------------------------------------

# Path to trained model
model_path = 'production_model.h5'

# File containing all trained class categories
class_file = "class_file.csv"

# File to hold the image path
image_list = "image_list.csv"

# Create the model
model = keras.models.load_model(model_path,
                                custom_objects=custom_objects)

if __name__ == '__main__':

    test_images = glob.glob("images/*.png")

    for test_image in test_images:
        preds, out_pil = run_inference(test_image)

    print("Done.")
