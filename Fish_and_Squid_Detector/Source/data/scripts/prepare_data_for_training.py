"""
Prepare data for training and inference for YOLOv5

For training, data is split into train, val and test

    80% train
    10% val
    10% test

For out-of-domain inference, all images are used and are placed in a separate
directory.

yaml files are created in each domain directory for training and out-of-domain testing.

Usage:
        $ python prepare_data_for_training.py path/to/data

NOTE: Some assumptions are made about the data locations
      Each directory with downloaded images and labels is under the 
        domain/species directory
      The images and labels for training will be created under
      the domain directory

      For example:
      downloaded images and labels are found in 
        /home/user/data/fathomnet/pre_2012/species/<images,labels>

      The images and labels directories for training will be created in
        /home/user/data/fathomnet/pre_2012/yolov5/images/<train,val,test>
        /home/user/data/fathomnet/pre_2012/yolov5/labels/<train,val,test>

      The images and labels directories for out-of-domain testing will be created in
	/home/user/data/fathomnet/pre_2012/yolov5/all/<images,labels>

      yaml files are created in
	/home/user/data/fathomnet/pre_2012/yolov5/

"""

import os
import sys
import numpy as np
import shutil

from pathlib import Path
from sklearn.model_selection import train_test_split

def make_dirs(dir=None):

    # Create directories for train, val, test and out-of-domain data
    dir = Path(dir)

    # train, val, test directories for training
    for p in dir / 'labels', dir / 'images':
        for s in 'train', 'val', 'test':
            ps = p / s
            ps.mkdir(parents=True, exist_ok=True)  # make dirs

    # out-of-domain data for object detection
    for p in dir / 'all' / 'labels', dir / 'all' / 'images':
        p.mkdir(parents=True, exist_ok=True)  # make dirs


def split_data_train_val_test(data_dir=None):

    species_list=["Chiroteuthis calyx", "Dosidicus gigas", "Gonatus onyx", 
                  "Sebastes", "Sebastolobus"]
    nspecies = len(species_list)

    # Find all YOLOv5 domain directories and annotations in data_dir
    domain_dirs = []

    for root, dirs, files in os.walk(data_dir):
        if "yolov5" in root and os.path.basename(root) == "yolov5":
            domain_dirs.append(os.path.dirname(root))
            make_dirs(root)


    # Prepare data for each domain
    for d in domain_dirs:
        dst_dir   = os.path.join(d, "yolov5")
    #   print('\n\nDST DIR: ', dst_dir)

        # Find species label directories
        label_dirs  = []
        for root, dirs, files in os.walk(d):
            if "label" in root and not ("yolov5" in root):
                label_dirs.append(root)

#       print('\n labels dir :', label_dirs)

        for lbl_dir in label_dirs:
#           print("lbl_dir ", lbl_dir)
            lbl_list  = [f for f in os.listdir(lbl_dir) if f.endswith(".txt")]
            lbl_array = np.array(lbl_list)
#           print(" size of lbl_array ", lbl_array.size)

            img_dir   = lbl_dir.replace("labels", "images")

            # Initially divide the data into 80% and 20%. 
            # 80% for training and remaining 20% for test and validation.
            train_data, rest_data = train_test_split(lbl_array, train_size=0.8, test_size=0.2)
        
            # Now you can split the remaining data into 50% each to have 
            # 10% validation and 10% test.
            val_data, test_data = train_test_split(rest_data, test_size=0.5)
        
            # Create sybolic links to training, val amd test data images in train
            # val and test  directories.
            # Symbolic links are created to save space and preserve all the original data 
            # in species directory.
            #
            # If you wish to copy the data or move it instead of creating symbolic links
            # replace all instances of os.symlink(src, dest) with 
            # shutil.copy(src, dest) or shutil.move(src, dest)
            #

            # Train data
            for f in train_data:
                # labels
                src = os.path.join(lbl_dir,f)
                dest = os.path.join(os.path.join(dst_dir, "labels/train"), f)

                # Some labels (and images) are in more than one species directory
                try:
                    os.symlink(src, dest)
                except:
                    pass
        
                # images
                img = f.replace("txt","png")
                src = os.path.join(img_dir, img)
                dest = os.path.join(os.path.join(dst_dir, "images/train"), img)
                try:
                    os.symlink(src, dest)
                except:
                    pass

            # Validation (val) data
            for f in val_data:
                # labels
                src = os.path.join(lbl_dir,f)
                dest = os.path.join(os.path.join(dst_dir, "labels/val"), f)
                try:
                    os.symlink(src, dest)
                except:
                    pass
        
                # images
                img = f.replace("txt","png")
                src = os.path.join(img_dir, img)
                dest = os.path.join(os.path.join(dst_dir, "images/val"), img)
                try:
                    os.symlink(src, dest)
                except:
                    pass


            # Test data
            for f in test_data:
                # labels
                src = os.path.join(lbl_dir,f)
                dest = os.path.join(os.path.join(dst_dir, "labels/test"), f)
                try:
                    os.symlink(src, dest)
                except:
                    pass
        
                # images
                img = f.replace("txt","png")
                src = os.path.join(img_dir, img)
                dest = os.path.join(os.path.join(dst_dir, "images/test"), img)
                try:
                    os.symlink(src, dest)
                except:
                    pass


            # For out-of-domain inference, we use all the images.
            # Out-of-domain data is created in all/labels and all/images

            # Out-of-domain data
            all_dir = os.path.join(dst_dir, "all")

            for f in lbl_array:
                # labels
                src = os.path.join(lbl_dir,f)
                dest = os.path.join(os.path.join(all_dir, "labels"), f)
                try:
                    os.symlink(src, dest)
                except:
                    pass
        
                # images
                img = f.replace("txt","png")
                src = os.path.join(img_dir, img)
                dest = os.path.join(os.path.join(all_dir, "images"), img)
                try:
                    os.symlink(src, dest)
                except:
                    pass


        # Create yaml file for each domain
        image_dir = os.path.join(dst_dir, 'images')

        train = os.path.join(str(image_dir),'train')
        val = os.path.join(str(image_dir),'val')
        test= os.path.join(str(image_dir),'test')

        line1 = "train: " + train + "  # train images \n"
        line2 = "val: " + val + "      # val images \n"
        line3 = "test: " + test + "    # test images \n\n"
        line4 = "# Classes \n"
        line5 = "nc: " + str(nspecies) + "  # number of clases\n"
        line6 = "names: " + str(species_list)

        # use all images for out of domain data
        all_img_dir = os.path.join(all_dir, 'images')
        line7 = "test: " + str(all_img_dir) + "    # test images \n\n"

        # Training yaml file
        yaml_name = os.path.basename(d) + ".yaml"
        yaml_file = os.path.join(dst_dir, yaml_name)
        with open(yaml_file, 'w') as output:
            output.writelines([ str(l) for l in [line1, line2, line3, line4, line5, line6] ])
        output.close()

        # yaml file for out-of-domain testing
        yaml_name = os.path.basename(d) + "_as_out_of_domain.yaml"
        yaml_file = os.path.join(dst_dir, yaml_name)
        with open(yaml_file, 'w') as output:
            output.writelines([ str(l) for l in [line1, line2, line7, line4, line5, line6] ])
        output.close()

            

if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print("Usage: python3 prepare_data_for_training.py\n /full/path/to/data//directory")
#       data_dir="/home/mimi/code/fathomnet/work/test_dir/data/years/pre_2012"
        data_dir="/home/mimi/code/fathomnet/work/test_dir/data/years"
#       exit()
    else:
        data_dir = sys.argv[1]

    print('data directory ', data_dir)
    split_data_train_val_test(data_dir)  # directory with *.json

