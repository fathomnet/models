FROM python:3.10

COPY fathomnet_config_v2_1280.yaml      \
     benthic_label_map.json             \
     model_final.pth                    \
     requirements1.txt                  \
     requirements2.txt                  \
     inference.py                       \
     tator.py                           \
     ./

RUN pip install -r requirements1.txt -r requirements2.txt \
    && apt-get update \
    && apt-get install ffmpeg libsm6 libxext6 -y

CMD [ "python", "-u", "./tator.py" ]
