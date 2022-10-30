import glob
import gradio as gr
from inference import *
from PIL import Image


def gradio_app(image_path):
    """A function that send the file to the inference pipeline, and filters
    some predictions before outputting to gradio interface."""

    predictions = run_inference(image_path)

    out_img = Image.fromarray(predictions.render()[0])

    return out_img


title = "MBARI Monterey Bay Benthic"
description = "Gradio demo for MBARI Monterey Bay Benthic: This model was " \
              "trained on 691 classes using 33,667 localized images from " \
              "MBARI’s Video Annotation and Reference System (VARS). Note: " \
              "only a subset of the VARS database is uploaded to FathomNet " \
              "because of institutional concept embargos. For training, " \
              "images were split 80/20 train/test. Classes were selected " \
              "because they are commonly observed concepts (primarily " \
              "benthic organisms, along with equipment and marine litter or " \
              "trash) within the Monterey Bay and Submarine Canyon system " \
              "from 500 to 4000 m deep. Many of these organisms will be seen " \
              "throughout the entire NE Pacific within the continental " \
              "slope, shelf, and abyssal regions. We used the PyTorch " \
              "framework and the yolov5 ‘YOLOv5x’ pretrained checkpoint to " \
              "train for 28 epochs with a batch size of 18 and image size of " \
              "640 pixels. DOI: 10.5281/zenodo.5539915 "

examples = glob.glob("images/*.png")

gr.Interface(gradio_app,
             inputs=[gr.inputs.Image(type="filepath")],
             outputs=gr.outputs.Image(type="pil"),
             enable_queue=True,
             title=title,
             description=description,
             examples=examples).launch()