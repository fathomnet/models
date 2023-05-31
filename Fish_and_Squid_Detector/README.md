### Description 🤖🎥🐠

Fish and Squid Detector was trained on data from [FathomNet](http://fathomnet.org/fathomnet/#/). 
Different models were trained with YOLOv5 on 6 classes using over 5600 annotated images from the 
FathomNet database collected in the Monterey Bay and surrounding regions of the coastal eastern 
Pacific. These classes were chosen due to the abundance of annotated images and the local interest 
in these species.  Five classes of squid and fish were used in primary analysis and reserved images 
of a siphonophore were used in a later analysis.

Data are partitioned into domains to examine the effects of distribution shifts on model 
performance. Partitions were designed to yield similar numbers of annotations for each focal class 
in each partition.

The first is a temporal partition. Annotated images of each of our focal classes are divided into 
images collected prior to 2012, and images collected from 2012 through the present. This 
partitioning resulted in Pre 2012 and Post 2012 domains.

The second partition is a spatial partition.  For each class, images are divided either by depth or 
by latitude and longitude to ensure that images of each class were divided into distinct spatial 
“regions,” defined arbitrarily as Region 1, and Region 2.

For more details about this model and the associated project please see:

Belcher, Byron T., Bower, Eliana H., Burford, Benjamin, Celis, Maria Rosa, Fahimipour, Ashkaan K., 
Guevara, Isabella L., Katija, Kakani, Manjunath, Anjana, Nelson, Samuel, Olivetti, Simone, 
Orenstein, Eric, Saleh, Mohamad H., Vaca, Brayan, Valladares, Salma, Hein, Stella A., & Hein, 
Andrew M. (2022). AI for the Ocean Fish and Squid Detector. https://doi.org/10.5281/zenodo.7430331


### Repository Status:
- In Progress `Dockerfile` ❌🛠️
- Working `inference` scripts and Notebooks ✅😀
- In Progress `inference` script to use with [TATOR](tator.io) ❌🛠️
- In Progress [Hugging Space Demo](https://huggingface.co/FathomNet) ❌🛠️

