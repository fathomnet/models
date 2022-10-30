## [YOLOv5 AWS Setup Tutorial](https://docs.ultralytics.com/environments/AWS-Quickstart/)

## EC2 Instance Setup
[EC2 Instance Types](https://aws.amazon.com/ec2/instance-types/)
- Chose a g4ad.xlarge because it's the cheapest GPU instance available (and can always be upgraded later). Pricing is about $0.38 per hour, or $9 per day.
- Trying to request it as a spot instance because it's cheaper (up to 70%). Unfortunately, there's a limit on our vCPU spot instance requests, so I submitted a support center request.
- Currently booted up a t2.2xlarge as a spot instance
- Copy private key > use PuTTY to make a public key version
- ssh into the EC2 instance

```
sudo yum install git
```

## Set up YOLOv5 dependencies
```
cd ~
git clone https://github.com/ultralytics/yolov5  # clone
cd yolov5
python3 pip install -r requirements.txt wandb  # install (add W&B for logging)
sudo yum install opencv  # install opencv library
```

## Downloading Data from Roboflow
[See steps 1.3 here](https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data)
Installed at `~/dataset_test_v1`

## Downloaded deepsea-detector repository

## [Download existing MBARI YOLOv5 model trained on FathomNet](https://zenodo.org/record/5539915#.YpU946jMJD8)
```curl -o https://zenodo.org/record/5539915/files/mbari-mb-benthic-33k.pt?download=1```

## Dataset Setup
TODO: Add note here about setting up the dataset.
One option is to specify download instructions in a file.
```
train: ../datasets/dataset_test_v1/train/images
val: ../datasets/dataset_test_v1/valid/images
test: ../datasets/dataset_test_v1/test/images

nc: 9
names: ['annelida', 'arthropoda', 'cnidaria', 'echinodermata', 'fish', 'mollusca', 'other-invertebrates', 'porifera', 'unidentified-biology']
```

## [Training the Model using Transfer Learning](https://github.com/ultralytics/yolov5/issues/1314)
- We use transfer learning so we don't have to retrain the entire ML model from scratch. This also helps because we have a very small dataset for training (7k images)
- `python3 train.py --freeze 10` freezes the first 9 layers, which serve as the backbone of the model (portions that should already be trained to recognized features).
- We also will freeze all the way up to layer 23, which is everything except for the final layer which makes classification predictions.
```
cd ~/deepsea-detector/models
cp mbari-mb-benthic-33k.pt deepsea-detector-yolo-v1.pt
cd ~/yolov5
python3 train.py --batch 48 --freeze 24 --weights models/deepsea-detector-yolo-v1.pt --data deepsea-detector-dataset-v1.yaml --epochs 12 --cache --img 640
```

## Links for later:
https://wandb.ai/onlineinference/YOLO/reports/YOLOv5-Object-Detection-on-Windows-Step-By-Step-Tutorial---VmlldzoxMDQwNzk4

