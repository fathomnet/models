#!/usr/bin/env python

import keras
import keras.preprocessing.image
from keras_retinanet.preprocessing.csv_generator import CSVGenerator
from keras_retinanet.models.resnet import custom_objects
from keras_retinanet.utils.keras_version import check_keras_version

import tensorflow as tf
import logging
import argparse
import os
import numpy as np
import pickle

logging.basicConfig(
    handlers=[logging.StreamHandler()],
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)

def parse_args():
    parser = argparse.ArgumentParser(description='Simple inference script for object detection.')
    parser.add_argument('model', help='Path to RetinaNet model.')
    parser.add_argument('test_path', help='Path to file containing list of inference images')
    parser.add_argument('class_file', help='Name of the class file to evaluate')
    parser.add_argument('--gpu', help='Id of the GPU to use (as reported by nvidia-smi).')
    parser.add_argument('--score-threshold', help='Threshold on score to filter detections with (defaults to 0.05).', default=0.05, type=float)
    parser.add_argument('--image_min_side', help='Minimum image side to rescale input to', default=1100, type=int)
    parser.add_argument('--image_max_side', help='Maximum image side to rescale input to', default=1650, type=int)
    parser.add_argument('--num_channels', type=int, default=3, help='Number of channels in input images')

    return parser.parse_args()

if __name__ == '__main__':
    # parse arguments
    args = parse_args()

    # make sure keras is the minimum required version
    check_keras_version()

    # optionally choose specific GPU
    if args.gpu:
        os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu
    keras.backend.tensorflow_backend.set_session(get_session())

    # create the model
    logger.info('Loading model, this may take a second...')
    model = keras.models.load_model(args.model, custom_objects=custom_objects)

    # create image data generator object
    test_image_data_generator = keras.preprocessing.image.ImageDataGenerator()

    # create a generator for testing data
    test_generator = CSVGenerator(
        args.test_path,
        args.class_file,
        None,
        test_image_data_generator,
        image_min_side=args.image_min_side,
        image_max_side=args.image_max_side,
        num_channels=args.num_channels)
    # start collecting results
    results = []
    image_ids = []
    for i in range(len(test_generator.image_names)):
        image = test_generator.load_image(i)
        image = test_generator.preprocess_image(image)
        image, scale = test_generator.resize_image(image)

        # run network
        _, _, detections = model.predict_on_batch(np.expand_dims(image, axis=0))

        # clip to image shape
        detections[:, :, 0] = np.maximum(0, detections[:, :, 0])
        detections[:, :, 1] = np.maximum(0, detections[:, :, 1])
        detections[:, :, 2] = np.minimum(image.shape[1], detections[:, :, 2])
        detections[:, :, 3] = np.minimum(image.shape[0], detections[:, :, 3])

        # correct boxes for image scale
        detections[0, :, :4] /= scale

        # change to (x, y, w, h) (MS COCO standard)
        detections[:, :, 2] -= detections[:, :, 0]
        detections[:, :, 3] -= detections[:, :, 1]

        # compute predicted labels and scores
        for detection in detections[0, ...]:
            label = int(detection[4])
            # append detections for each positively labeled class
            if float(detection[5 + label]) > args.score_threshold:
                image_result = {
                    'image_id'    : test_generator.image_names[i],
                    'category_id' : test_generator.label_to_name(label),
                    'scores'      : [float(det) for i,det in 
                                     enumerate(detection) if i >= 5],
                    'bbox'        : (detection[:4]).tolist(),
                }
                # append detection to results
                results.append(image_result)
        # append image to list of processed images
        image_ids.append(test_generator.image_names[i])

        # print progress
        logger.info('{}/{}'.format(i, len(test_generator.image_names)))
    out_name = '{}_predict_results_{}.pickle'.format(os.path.splitext(args.test_path)[0],str(args.score_threshold).split(".")[-1])
    pickle.dump(results,open(out_name,'wb'))