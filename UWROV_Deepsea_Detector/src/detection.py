""" Code adapted from the tryolabs/norfair project
(https://github.com/tryolabs/norfair/blob/master/demos/yolov5/yolov5demo.py)
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Union, List, Optional
import csv

import cv2
import norfair
import numpy as np
import torch
import yolov5

max_distance_between_points: int = 30
PREVIEW_WINDOW_NAME = "image"
classifications: List[str] = ['annelida', 'arthropoda', 'cnidaria', 'echinodermata', 'fish',
                              'mollusca', 'other-invertebrates', 'porifera', 'unidentified-biology']

class OrganismDetection:
    "Data class for organism detections."

    def __init__(self, num_id:int, classification:str) -> None:
        self.num_id: int = num_id
        self.classification: str = classification
        self.frames: List[int] = []
    
    def add_detection(self, frame:int):
        "Registers a detection, including the frame of appearance and confidence level."
        self.frames.append(frame)

    def get_first_last_frame(self) -> Tuple[int, int]:
        "Returns the first and last frame of appearance as a tuple."
        return (self.frames[0], self.frames[len(self.frames) - 1])    


class YOLO:
    "Wrapper class for loading and running YOLO model"
    def __init__(self, model_path: str, device: Optional[str] = None):
        if device is not None and "cuda" in device and not torch.cuda.is_available():
            raise Exception(
                "Selected device='cuda', but cuda is not available to Pytorch."
            )
        # automatically set device if its None
        elif device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        # load model
        self.model = yolov5.load(model_path, device=device)

    def __call__(
        self,
        img: Union[str, np.ndarray],
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        image_size: int = 720,
        classes: Optional[List[int]] = None
    ) -> torch.Tensor:

        self.model.conf = conf_threshold
        self.model.iou = iou_threshold
        if classes is not None:
            self.model.classes = classes
        detections = self.model(img, size=image_size)  # pylint: disable=not-callable
        return detections


def euclidean_distance(detection, tracked_object):
    """Returns euclidean distance between two points."""
    return np.linalg.norm(detection.points - tracked_object.estimate)


def center(points):
    """Returns the center coordinates of a series of points."""
    return [np.mean(np.array(points), axis=0)]


def format_seconds(seconds: int) -> str:
    "Formats a duration in seconds into a string format. (H:MM:SS or MM:SS)"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = (seconds % 60)
    if h > 0:
        return "%d:%02d:%02d" % (h, m, s)
    else:
        return "%02d:%02d" % (m, s)

def yolo_detections_to_norfair_detections(
    yolo_detections: torch.Tensor,
    track_points: str = 'bbox'  # bbox or centroid
) -> List[norfair.Detection]:
    """Converts detections_as_xywh to norfair detections.
    Label is the classification of the detection.
    """
    norfair_detections: List[norfair.Detection] = []

    if track_points == 'centroid':
        detections_as_xywh = yolo_detections.xywh[0]
        for detection_as_xywh in detections_as_xywh:
            centroid = np.array(
                [
                    detection_as_xywh[0].item(),
                    detection_as_xywh[1].item()
                ]
            )
            scores = np.array([detection_as_xywh[4].item()])
            label = classifications[int(detection_as_xywh[5].item())]
            norfair_detections.append(
                norfair.Detection(points=centroid, scores=scores, label=label)
            )
    elif track_points == 'bbox':
        detections_as_xyxy = yolo_detections.xyxy[0]
        for detection_as_xyxy in detections_as_xyxy:
            bbox = np.array(
                [
                    [detection_as_xyxy[0].item(), detection_as_xyxy[1].item()],
                    [detection_as_xyxy[2].item(), detection_as_xyxy[3].item()]
                ]
            )
            label = classifications[int(detection_as_xyxy[5].item())]
            scores = np.array([detection_as_xyxy[4].item(),
                              detection_as_xyxy[4].item()])
            norfair_detections.append(
                norfair.Detection(points=bbox, scores=scores, label=label)
            )

    return norfair_detections


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Track objects in a video.")
    parser.add_argument("files", type=str, nargs="+",
                        help="Video files to process")
    parser.add_argument("--detector_path", type=str,
                        default="yolov5m6.pt", help="YOLOv5 model path")
    parser.add_argument("--img_size", type=int, default="640",
                        help="YOLOv5 inference size (pixels)")
    parser.add_argument("--conf_thres", type=float, default="0.25",
                        help="YOLOv5 object confidence threshold")
    parser.add_argument("--iou_thresh", type=float,
                        default="0.45", help="YOLOv5 IOU threshold for NMS")
    parser.add_argument('--classes', nargs='+', type=int,
                        help='Filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument("--device", type=str, default=None,
                        help="Inference device: 'cpu' or 'cuda'")
    parser.add_argument("--period", type=int, default=1,
                        help="The period (in frames) with which the detector should be run.")
    parser.add_argument("--output_csv", type=str, default="out.csv",
                        help="Output path for the tracking data CSV file.")
    parser.add_argument("--output_video", type=str, default="out.mp4",
                        help="Output video file if only running one file at a time. Ignored if multiple video files are provided. Note that an existing file will not be overwritten-- a copy with a number suffix (ex: video(1).mp4) will be written instead.")
    parser.add_argument("--output_folder", type=str, default="./",
                        help="Output folder used when multiple files are provided. Note that existing files will not be overwritten-- copies with a number suffix (ex: video(1).mp4) will be written instead.")
    parser.add_argument("--output_video_prefix", type=str, default="out_",
                        help="Prefix to add to each processed video name when multiple video files are provided. Default is 'out_'")
    parser.add_argument("--show_preview", action="store_true",
                        help="Show a preview of detections in real time. Do not use in python notebooks.")
    parser.add_argument("--show_classes", action="store_true",
                        help="Include the class labels in the output video(s).")

    args = parser.parse_args()
    
    # Check file inputs to make sure they actually exist.
    if not Path(args.detector_path).exists():
        raise FileNotFoundError("Could not find YOLOv5 detector '{}'".format(args.detector_path))
    for input_path in args.files:
        if not Path(input_path):
            raise FileNotFoundError("Could not find video input path '{}'".format(args.detector_path))
    if not Path(args.output_folder).is_dir():
        raise FileNotFoundError("Could not find directory '{}'".format(args.output_folder))

    model = YOLO(args.detector_path, device=args.device)

    video_path_to_data: Dict[str, Dict[int, OrganismDetection]] = {}

    for input_path in args.files:
        start_time = datetime.now()
        # Get output path name
        file_attempt = 1
        output_name = ""
        if len(args.files) > 1:
            output_name = Path("{}/{}{}{}".format(
                    args.output_folder,
                    args.output_video_prefix,
                    Path(input_path).stem,
                    Path(input_path).suffix
                ))
        else:
            output_name = Path(args.output_video)
        # Increment the (1), (2), (3) file numbering if file exists
        while(output_name.exists()):
            if len(args.files) > 1:
                output_name = Path("{}/{}{}({}){}".format(
                    args.output_folder,
                    args.output_video_prefix,
                    Path(input_path).stem,
                    file_attempt,
                    Path(input_path).suffix
                ))
            else:
                output_name = Path(args.output_video).parent/Path("{}({}){}".format(
                    Path(args.output_video).stem,
                    file_attempt,
                    Path(args.output_video).suffix
                ))
            file_attempt += 1


        video = norfair.Video(input_path=input_path,
                              output_path=str(output_name))

        # Get video metadata (fps, frames, etc.)
        video_capture = cv2.VideoCapture(input_path)
        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(video_capture.get(cv2.CAP_PROP_FPS))
        duration = total_frames / fps

        filename = Path(input_path).name

        tracker = norfair.Tracker(
            distance_function=euclidean_distance,
            distance_threshold=max_distance_between_points,
        )
        paths_drawer = norfair.Paths(center, attenuation=0.01)

        track_id_to_data: Dict[int, OrganismDetection] = {}

        for i, frame in enumerate(video):
            if i % args.period == 0:
                yolo_detections = model(
                    frame,
                    conf_threshold=args.conf_thres,
                    iou_threshold=args.iou_thresh,
                    image_size=args.img_size,
                    classes=args.classes
                )
                norfair_detections = yolo_detections_to_norfair_detections(
                    yolo_detections, track_points="bbox")
                tracked_objects = tracker.update(
                    detections=norfair_detections, period=args.period)
                # norfair.draw_boxes(frame, norfair_detections)
            else:
                tracked_objects = tracker.update()

            for obj in tracked_objects:
                if obj.id not in track_id_to_data:
                    # First time this object has been identified, so we save it.
                    track_id_to_data[obj.id] = OrganismDetection(obj.id, obj.label)
                track_id_to_data[obj.id].add_detection(i)

            if args.show_classes:
                norfair.draw_tracked_boxes(frame, tracked_objects, border_colors=[(0, 255, 255)], border_width=1, draw_labels=True)
            else:
                norfair.draw_tracked_boxes(frame, tracked_objects, border_colors=[(0, 255, 255)], border_width=1)
            frame = paths_drawer.draw(frame, tracked_objects)
            video.write(frame)

            if args.show_preview:
                cv2.imshow(PREVIEW_WINDOW_NAME, frame)
                curr_time = datetime.now()
                time_per_frame = (curr_time - start_time) / (i + 1)
                remaining_time_s = (total_frames - (i + 1)) * time_per_frame.total_seconds()

                name = "{filename}: {curr_duration}/{total_duration} ({percent_completion}% complete, est. {remaining_time} remaining)".format(
                    filename=filename,
                    curr_duration=format_seconds((i + 1) / fps),
                    total_duration=format_seconds(total_frames / fps),
                    percent_completion=str(int(((i + 1) / total_frames * 100))),
                    remaining_time=format_seconds(remaining_time_s)
                )
                cv2.setWindowTitle(PREVIEW_WINDOW_NAME, name)
        # Save all the data for this video
        video_path_to_data[input_path] = track_id_to_data

    # Finished traversing frames, so we write out CSV tracking data.
    with open(args.output_csv, 'w', newline='') as csv_file:
        fieldnames = ['src_video', 'classification', 'first_frame', 'first_timestamp', 'last_frame', 'last_timestamp']
        writer = csv.DictWriter(
            csv_file, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for input_path in video_path_to_data:
            track_id_to_data = video_path_to_data[input_path]
            video_filename = Path(input_path).name

            for organism_detection in track_id_to_data.values():
                # Write out each tracked object as its own row.
                # classification, starting frame, ending frame
                first_frame, last_frame = organism_detection.get_first_last_frame()
                writer.writerow({
                    'src_video': video_filename,
                    'classification': organism_detection.classification,
                    'first_frame': first_frame,
                    'first_timestamp': format_seconds(first_frame // fps),
                    'last_frame': last_frame,
                    'last_timestamp': format_seconds(last_frame // fps),
                })

    # Close the preview window
    if args.show_preview:
        # Need a try here because norfair video will destroy all open cv2 windows, but it's not a
        # documented behavior and might be changed in the future.
        try:
            cv2.destroyWindow(PREVIEW_WINDOW_NAME)
        except cv2.error:
            pass
