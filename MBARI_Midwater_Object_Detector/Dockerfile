FROM cvisionai/retinanet:latest

RUN apt-get update

# Not necessary, but used for the Gradio demo
RUN apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get -y install python3.7

COPY . ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD [ "python", "-u", "./tator_inference.py" ]