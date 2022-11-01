import glob
import gradio as gr
from inference import *


def gradio_app(image_path):
    """A function that send the file to the inference pipeline, and filters
    some predictions before outputting to gradio interface."""

    predictions, out_pil = run_inference(image_path)

    return out_pil


title = "MBARI Midwater Object Detector"
description = "Gradio demo for MBARI Midwater Object Detector: A fine tuned " \
              "RetinaNet model with a ResNet-50 backbone trained to identify " \
              "16 midwater classes. The 29,327 training images were " \
              "collected in Monterey Bay by two imaging systems developed at " \
              "the Monterey Bay Aquarium Research Institute. The monochrome " \
              "and 3-channel color images contain a total of 34," \
              "071 localizations that were split into 90/10 train/validation " \
              "sets. The full set of images will be loaded into FathomNet " \
              "and a list of persistent URLs will be added to a future " \
              "version of this repository. DOI: 10.5281/zenodo.5942597 "

examples = glob.glob("images/*.png")

gr.Interface(gradio_app,
             inputs=[gr.inputs.Image(type="filepath")],
             outputs=gr.outputs.Image(type="pil"),
             enable_queue=True,
             title=title,
             description=description,
             examples=examples).launch()
