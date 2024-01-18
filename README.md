# ECT_of_leaves

Directory created by Nathan Willey Spring 2023 for pre-processing of leaf shape data into Euler Characteristic Transform data. This document serves to outline the data pipeline created here and the use of all the included files/functions defined. Please contact me for any missing information or help!

Raw leaf data was found here: https://figshare.com/articles/dataset/Leaf_coordinates_zip/5056441/1 \
Currently, leaf ECT data is stored at `/mnt/research/morphology_lab/Results/ECT_of_leaves/leaf_ect`\
Intermediate contour data is stored at `/mnt/research/morphology_lab/Results/ECT_of_leaves/contour_data`\
This directory is stored locally on the HPCC at `/mnt/research/morphology_lab/Code/ECT_of_leaves`

Functions used are stored in `ect.py`

## Data Pipeline

### 1. Original Data Format

Leaf data is stored as point-clouds and the original data has both a centered and non-centered set of coordinates. We only ever consider the centered set of points. _Most_ leaf data point clouds are stored in "contour form", i.e. point 0 and the last point coincide and points between them go around the leaf contour positively oriented. This is the "correct" representation as we assume all leaves to be single connected component contours (i.e. total E.C. 0).
Since the data was sourced heterogenously, some leaves instead have coordinates ordered by increasing x coordinate. Furthermore, some leaves have holes in the middle and those are (generally) stored as increasing x coordinate of the main body, then increasing x coordinate of any holes. 

We would like the final data format to be networks with E.C. 0 for analysis via ECT. 
The first step of the data pipeline then is transforming these non-uniformly labeled pointclouds into this type of data.
Grape leaves and Leafsnap were the only types to have > 5% of data mislabeled and thus the goal is to recover this data into contours rather than just throwing them away.

### 2. Contour Reordering

The transformation from pointcloud to contour-ordered labeling is as follows:

If first and last point coincide (leaf[0] == leaf[-1]) then we __assume__ the leaf is correctly labeled and do nothing to it

Else: 
1. Make a 2 Nearest Neighbor graph out of the pointcloud data
2. Choosing leaf[0] and look for a walk around the leaf that starts and ends at this point that walks through at least half of the points
3. If chosen, relabel those points according to the walk found
4. If no walk is found from leaf[0], look at leaf[10 * k] (for interate k) and try to start the walk from there 

This algorithm is performed by `contour_order()`

A result of this algorithm is that smaller disconnected components are lost\
Overall this algorithm transforms ~80% of the Leafsnap data and ~60% of the grapevine data that overwise would have been lost due to mislabeling (~5% of the total dataset is still thrown out since it is unable to be reconstructed with 2NN graph)
A full readout of data % mislabeled, recovered, and lost can be found in `data_stats.csv`
A few examples of reordered leaves as well as unrecoverable ones can be found at <https://imgur.com/a/ZRc2D3V>

### 3. ECT Matrix Creation 

The final data form we desire is an Euler Characteristic Transform with d directions. We take directions to be linearly spaced between 0 and 2pi. These ECTs are represented as d concatenated Euler Characteristic Curves with resolution T, thus each ECT is a d * T length vector

Computation of ECCs is done assuming the contour structure of the data (input is contour_data). At a given height value we must only count the number of breaks in the label order to determine the number of connected components (since there is at most one hole, when all data points are present). This is done in `contour_ect()`

I store these in "ECT matrices" (3D np arrays) where each ECT[i,j] is an ECT with a different number of linearly spaced directions and resolution determined by i and j respectively.\ In use it is expected that for each leaf only one ECT[i,j] is used. ECTs are padded with nans at the end (just to make the 3D np array storage work), these should be dropped in use. ECT matrix creation is handled by `compute_ect.py`.\
Current indexing is as follows:

N_ANGLES = [2, 4, 8, 16, 32]\
RESOLUTIONS = [10, 20, 30, 40, 50]

example: ECT[3,4] gives the ECT with 16 linearly spaced directions on S1 and 50 linearly spaced heights over the leaf for each direction (resolution=50)

## Files 

Refer to this section if any data creation needs to be rerun or modified 

`contour_order.py`\
Given a directory of leaf point-cloud data (from the given link), runs the above algorithm to check all data, transform labels if needed, and save as npy files in ./contour_data/ \
Run this _one_ script, should only ever need to change the name of the input directory in the script 

`write_ect_jobs.py`\
Initalizes parallelization of ECT computation on all datasets by creating a job for each subdirectory.\ 
Given a directory of data in the form of contour_data from the above function, creates jobs for each subdirectory (leaf type) that run `compute_ect.py` on the subdirectory. Job sbatch files are stored in `./submit/` and created `run.sh` submits all created .sb files. 

To use: Check to see that data dir, output dir, sb dir, and HR/MEMORY for jobs is correct, then run this script to create all the jobs. Then on an HPCC node, run `/submit/run.sh` to submit all slurm jobs

`compute_ect.py`\
Script to be run by jobs created by `write_ect_jobs.py`. Creates an ECT matrix for a given subdirectory of contour data with a specified array of the number of linearly spaced angles and the threshold values (see #3 above). Should never need to be manually ran, but one DOES need to change the number of angles and thresholdings in here before running ect jobs!

`ect.py`\
Mini-package holding functions used in all scripts 

## TL;DR for creating new ECT matrices 
(Assumes that contour data is all okay-- if not refer to files section to recreate this data)

1. Go into `compute_ect.py` and change the array of n_angles and thresholding to whatever you'd like
2. Go into `write_ect_jobs.py` and make sure input and output directories are okay as well as enough time/memory is given in each job
3. Run `run.sh` in `/submit`
4. ECT matrices output to `/leaf_ect/`

