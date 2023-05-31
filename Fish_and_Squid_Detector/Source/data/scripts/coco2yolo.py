#
"""
Convert custom FathomNet dataset from COCO format to YOLO format

Reads a directory to search for COCO json files. 
For each *.json file found, the code modifies the category and category_id 
in the json to have the classes for each species as needed in our analysis.
The code then converts the json files into YOLO format.

Usage:
	$ python coco2yolo.py path/to/coco/json/files
"""

import os
import sys
import json

import numpy as np
import shutil

from pathlib import Path

# COCO species classes for training FathomNet fish, squid and jellies data
# NOTE: Nanomia bijuga is used as a distractor class in a separate experiment
#       with only Chiroteuthis calyx. So the species id will be 
#	1 for Chiroteuthis calyx
#	2 for Nanomia bijuga
#
species_dict = {
    "Chiroteuthis calyx": 1,
    "Dosidicus gigas": 2,
    "Gonatus onyx": 3,
    "Sebastes": 4,
    "Sebastes diploproa": 4,
    "Sebastes melanostomus": 4,
    "Sebastolobus": 5,
    "Nanomia bijuga": 2
}


def make_dirs(dir='new_dir/'):
    # Create folders
    dir = Path(dir)
    lbl_dir = dir/'labels'
    if lbl_dir.exists():
        shutil.rmtree(lbl_dir)  # delete labels dir
    for p in dir, dir / 'labels':
        p.mkdir(parents=True, exist_ok=True)  # make dir
    return dir


def modify_species_id(json_file, data):

    # Create dictionary with original categories from json_file
    # {id: 'name'}
    # change id in categories (species)
    species_orig_dict={}
    for x in data["categories"]:
        species_orig_dict[x["id"]] = x["name"]
        x["id"] = species_dict[x["name"]]

    # change category_id value
    for x in data['annotations']:
        x['category_id'] = species_dict[species_orig_dict[x['category_id']]]

    # Write changes to coco json file
    f = open(json_file, "w+")
    f.write(json.dumps(data, indent=1))
    f.close()

    return(data)



def convert_coco_json(data_dir=None):

    # Find all coco json annotation files
    coco_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".json"):
                coco_files.append(os.path.join(root, file))

    for json_file in coco_files:
        json_dir = os.path.dirname(json_file)
        save_dir = make_dirs(json_dir)  # output directory
        fn = os.path.join(save_dir, "labels")
        if not os.path.exists(fn):
            fn.mkdir()

        with open(json_file) as f:
            coco_data = json.load(f)
        f.close()

        # Modify species ids in COCO json file
        coco_data = modify_species_id(json_file, coco_data)

        # Create image dict
        images = {'%g' % x['id']: x for x in coco_data['images']}

        # Write labels file
        for x in coco_data['annotations']:
            if x['iscrowd']:
                continue

            img = images['%g' % x['image_id']]
            h, w, f = img['height'], img['width'], img['file_name']

            # The COCO box format is [top left x, top left y, width, height]
            box = np.array(x['bbox'], dtype=np.float64)
            box[:2] += box[2:] / 2  # xy top-left corner to center
            box[[0, 2]] /= w  # normalize x
            box[[1, 3]] /= h  # normalize y

           # Write YOLO label
            if box[2] > 0 and box[3] > 0:  # if w > 0 and h > 0
                cls  = x['category_id'] - 1  # YOLO class (species_id-1)
                line = cls, *box  # cls, box
#               with open((fn / f).with_suffix('.txt'), 'a') as file:
                with open(os.path.join(fn ,f.replace('png', 'txt')), 'a') as file:
                    file.write(('%g ' * len(line)).rstrip() % line + '\n')

    
if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print("Usage: python3 coco2yolo.py\n /full/path/to/coco/annotation/top/directory")
        exit()
    else:
        coco_dir = sys.argv[1]

    print('Top directory to look for json files ', coco_dir)
    convert_coco_json(coco_dir)  # directory with *.json

