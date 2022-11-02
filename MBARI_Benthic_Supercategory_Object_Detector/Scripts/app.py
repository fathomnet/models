try:
    import detectron2
except:
    import os
    os.system("pip install 'git+https://github.com/facebookresearch/detectron2.git'")


from MBARI_Benthic_Supercategory_Object_Detector.Scripts.inference import *
import gradio as gr
import glob


def gradio_app(image_path):
    """Helper function to run inference on provided image"""

    predictions, out_pil = run_inference(image_path)

    return out_pil


# -----------------------------------------------------------------------------
# GRADIO APP
# -----------------------------------------------------------------------------

title = "MBARI Monterey Bay Benthic Supercategory"
description = "Gradio demo for MBARI Monterey Bay Benthic Supercategory: This " \
              "is a RetinaNet Models fine-tuned from the Detectron2 object " \
              "detection platform's ResNet backbone to identify 20 benthic " \
              "supercategories drawn from MBARI's remotely operated vehicle " \
              "image data collected in Monterey Bay off the coast of Central " \
              "California. The data is drawn from FathomNet and consists of " \
              "32779 Images that contain a total of 80683 localizations. The " \
              "Models was trained on an 85/15 train/validation split at the " \
              "image level. DOI: 10.5281/zenodo.5571043. "

examples = glob.glob("../Images/*.png")

gr.Interface(gradio_app,
             inputs=[gr.inputs.Image(type="filepath")],
             outputs=gr.outputs.Image(type="pil"),
             enable_queue=True,
             title=title,
             description=description,
             examples=examples).launch()
