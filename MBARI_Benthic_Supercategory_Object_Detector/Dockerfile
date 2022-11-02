FROM python:3.10

RUN apt-get update \
    && apt-get install ffmpeg  \
    libsm6  \
    libxext6 -y

COPY . ./app

RUN pip install -r ./app/requirements.txt
RUN python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'

CMD [ "python", "-u", "./app/Scripts/inference_tator.py" ]
