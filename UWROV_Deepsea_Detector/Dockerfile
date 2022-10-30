FROM python:3.7

RUN apt-get update \
    && apt-get install ffmpeg libsm6 libxext6 -y

RUN pip install yolov5 tator gradio

COPY . ./

CMD [ "python", "-u", "./tator_inference.py" ]