FROM cvisionai/retinanet:latest

RUN apt-get update

COPY . ./app

RUN pip install --upgrade pip

RUN pip install -r ./app/requirements.txt

CMD [ "python", "-u", "./app/Scripts/tator_inference.py" ]