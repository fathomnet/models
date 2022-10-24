FROM python:3.10

COPY fathomnet_config_v2_1280.yaml      \
     benthic_label_map.json             \
     model_final.pth                    \
     requirements1.txt                  \
     images                             \
     ./

RUN pip install -r requirements1.txt
RUN python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
RUN apt-get update \
    && apt-get install ffmpeg libsm6 libxext6 -y

COPY inference.py                       \
     tator.py                           \
     ./

CMD [ "python", "-u", "./tator.py" ]
