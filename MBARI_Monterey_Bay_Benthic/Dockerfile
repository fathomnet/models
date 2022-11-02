FROM python:3.7

RUN apt-get update \
    && apt-get install ffmpeg libsm6 libxext6 -y

COPY . ./app

RUN pip install -r ./app/requirements.txt

CMD [ "python", "-u", "./app/Scripts/tator_inference.py" ]