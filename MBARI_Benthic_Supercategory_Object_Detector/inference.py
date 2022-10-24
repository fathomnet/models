import os
import glob

import numpy as np
import detectron2
import torchvision
import cv2
import torch

from detectron2 import model_zoo
from detectron2.data import Metadata
from detectron2.structures import BoxMode
from detectron2.utils.visualizer import Visualizer
from detectron2.config import get_cfg
from detectron2.utils.visualizer import ColorMode
from detectron2.modeling import build_model
import detectron2.data.transforms as T
from detectron2.checkpoint import DetectionCheckpointer

import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# CONFIGS - loaded just the one time when script is first ran to save time.
#
# This is where you will set all the relevant config file and weight file
# variables:
# CONFIG_FILE - Training specific config file for fathomnet
# WEIGHTS_FILE - Path to the model with fathomnet weights
# NMS_THRESH - Set a nms threshold for the all boxes results
# SCORE_THRESH - This is where you can set the model score threshold

CONFIG_FILE = "fathomnet_config_v2_1280.yaml"
WEIGHTS_FILE = "model_final.pth"
NMS_THRESH = 0.45  #
SCORE_THRESH = 0.3  #

# A metadata object that contains metadata on each class category; used with
# Detectron for linking predictions to names and for visualizations.
fathomnet_metadata = Metadata(
    name='fathomnet_val',
    thing_classes=[
        'Anemone',
        'Fish',
        'Eel',
        'Gastropod',
        'Sea star',
        'Feather star',
        'Sea cucumber',
        'Urchin',
        'Glass sponge',
        'Sea fan',
        'Soft coral',
        'Sea pen',
        'Stony coral',
        'Ray',
        'Crab',
        'Shrimp',
        'Squat lobster',
        'Flatfish',
        'Sea spider',
        'Worm']
)

# This is where the model parameters are instantiated. There is a LOT of
# nested arguments in these yaml files, and the merging of baseline defaults
# plus dataset specific parameters.
base_model_path = "COCO-Detection/retinanet_R_50_FPN_3x.yaml"

cfg = get_cfg()
cfg.MODEL.DEVICE = 'cpu'
cfg.merge_from_file(model_zoo.get_config_file(base_model_path))
cfg.merge_from_file(CONFIG_FILE)
cfg.MODEL.RETINANET.SCORE_THRESH_TEST = SCORE_THRESH
cfg.MODEL.WEIGHTS = WEIGHTS_FILE

# Loading of the model weights, but more importantly this is where the model
# is actually instantiated as something that can take inputs and provide
# outputs. There is a lot of documentation about this, but not much in the
# way of straightforward tutorials.
model = build_model(cfg)
checkpointer = DetectionCheckpointer(model)
checkpointer.load(cfg.MODEL.WEIGHTS)
model.eval()

# Create two augmentations and make a list to iterate over
aug1 = T.ResizeShortestEdge(short_edge_length=[cfg.INPUT.MIN_SIZE_TEST],
                            max_size=cfg.INPUT.MAX_SIZE_TEST,
                            sample_style="choice")

aug2 = T.ResizeShortestEdge(short_edge_length=[1080],
                            max_size=1980,
                            sample_style="choice")

augmentations = [aug1, aug2]

# We use a separate NMS layer because initially detectron only does nms intra
# class, so we want to do nms on all boxes.
post_process_nms = torchvision.ops.nms
# -----------------------------------------------------------------------------


def run_inference(test_image):
    """This function runs through inference pipeline, taking in a single
    image as input. The image will be opened, augmented, ran through the
    model, which will output bounding boxes and class categories for each
    object detected. These are then passed back to the calling function."""

    # Load the image, get the height and width. Iterate over each
    # augmentation: do the augmentation, run the model, perform nms
    # thresholding, instantiate a useful object for visualizing the outputs.
    # Saves a list of outputs objects
    img = cv2.imread(test_image)
    im_height, im_width, _ = img.shape
    v_inf = Visualizer(img[:, :, ::-1],
                       metadata=fathomnet_metadata,
                       scale=1.0,
                       instance_mode=ColorMode.IMAGE_BW)

    insts = []

    # iterate over input augmentations (apply resizing)
    for augmentation in augmentations:
        im = augmentation.get_transform(img).apply_image(img)

        # pre-process image by reshaping and converting to tensor
        # pass to model, which outputs a dict containing info on all detections
        with torch.no_grad():
            im = torch.as_tensor(im.astype("float32").transpose(2, 0, 1))
            model_outputs = model([{"image": im,
                                    "height": im_height,
                                    "width": im_width}])[0]

        # populate list with all outputs
        for _ in range(len(model_outputs['instances'])):
            insts.append(model_outputs['instances'][_])

    # TODO explore the outputs to determine what needs to be passed to tator.py
    # Concatenate the model outputs and run NMS thresholding on all output;
    # instantiate a dummy Instance object to concatenate the instances
    model_inst = detectron2.structures.instances.Instances([im_height,
                                                            im_width])

    xx = model_inst.cat(insts)[
        post_process_nms(model_inst.cat(insts).pred_boxes.tensor,
                         model_inst.cat(insts).scores,
                         NMS_THRESH).to("cpu").tolist()]


    print(test_image + ' - Number of predictions:', len(xx))
    out_inf_raw = v_inf.draw_instance_predictions(xx.to("cpu"))

    if False:

        os.makedirs("predictions", exist_ok=True)

        plt.figure(figsize=(20,10))
        plt.title("Predictions: " + str(len(xx)) + "    Image: " + test_image)
        plt.subplot(1, 2, 1)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.subplot(1, 2, 2)
        plt.imshow(out_inf_raw.get_image())
        plt.savefig("predictions/" + os.path.basename(test_image))

    # Converting the predictions as output by Detectron2, to a TATOR format.
    predictions = convert_predictions(xx, v_inf.metadata.thing_classes)

    return predictions


def convert_predictions(xx, thing_classes):
    """Helper funtion to post-process the predictions made by Detectron2
    codebase to work with TATOR input requirements."""

    predictions = []

    for _ in range(len(xx)):

        # Obtain the first prediction, instance
        instance = xx.__getitem__(_)

        # Map the coordinates to the variables
        x, y, x2, y2 = map(float, instance.pred_boxes.tensor[0])
        w, h = x2 - x, y2 - y

        # Use class list to get the common name (string); get confidence score.
        class_category = thing_classes[int(instance.pred_classes[0])]
        confidence_score = float(instance.scores[0])

        # Create a spec dict for TATOR
        prediction = {'x': x,
                      'y': y,
                      'width': w,
                      'height': h,
                      'class_category': class_category,
                      'confidence': confidence_score}

        predictions.append(prediction)

    return predictions


if __name__ == "__main__":

    # For demo purposes: run through a couple of test
    # images and then output the predictions in a folder.
    test_images = glob.glob("images/*.png")

    for test_image in test_images:
        predictions = run_inference(test_image)

    print("Done.")

