FROM cvisionai/openem_lite:latest

RUN apt update
COPY retinanet-classify-image.py /scripts/retinanet-classify-image.py
COPY production_model.h5 /scripts/production_model.h5
COPY class_file.csv /scripts/class_file.csv
COPY example_inference.csv /scripts/example_inference.csv

WORKDIR /scripts

