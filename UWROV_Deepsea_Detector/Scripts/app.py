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


title = "UWROV Deepsea Detector"
description = "Gradio demo for UWROV Deepsea Detector: Developed by Peyton " \
              "Lee, Neha Nagvekar, and Cassandra Lam as part of the " \
              "Underwater Remotely Operated Vehicles Team (UWROV) at the " \
              "University of Washington. Deepsea Detector is built on " \
              "MBARI's Monterey Bay Benthic Object Detector, which can also " \
              "be found in FathomNet's Model Zoo. The Models is trained on " \
              "data from NOAA Ocean Exploration and FathomNet, " \
              "with assistance from WoRMS for organism classification. All " \
              "the Images and associated annotations we used can be found in " \
              "our Roboflow project. "

examples = glob.glob("../Images/*.png")

gr.Interface(gradio_app,
             inputs=[gr.inputs.Image(type="filepath")],
             outputs=gr.outputs.Image(type="pil"),
             enable_queue=True,
             title=title,
             description=description,
             examples=examples).launch()