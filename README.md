# ECT_of_leaves

Directory created by Nathan Willey Spring 2023 for pre-processing of leaf shape data into Euler Characteristic Transform data. This document serves to outline the data pipeline created here and the use of all the included files/functions defined. Please contact me for any missing information or help!

Raw leaf data was found here: https://figshare.com/articles/dataset/Leaf_coordinates_zip/5056441/1
Currently, leaf ECT data is stored at /mnt/research/morphology_lab/Results/ECT_of_leaves/leaf_ect and intermediate contour data is stored at /mnt/research/morphology_lab/Results/ECT_of_leaves/contour_data 

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
4. If no walk is found from leaf[0], look at leaf[10 * k] and try to start the walk from there 

This algorithm is performed by `contour_order()`

A result of this algorithm is that smaller disconnected components are lost 
Overall this algorithm transforms ~80% of the Leafsnap data and ~60% of the grapevine data that overwise would have been lost due to mislabeling (~5% of the total dataset is still thrown out since it is unable to be reconstructed with 2NN graph)
A full readout of data % mislabeled, recovered, and lost can be found in `data_stats.csv`

### 3. ECT Matrix Creation 

The final data form we desire is an Euler Characteristic Transform, represented as d concatenated Euler Characteristic Curves with resolution T, thus each ECT is a d * T length vector

Computation of ECCs is done assuming the contour structure of the data. At a given height value we must only count the number of breaks in the label order to determine the number of connected components (since there is at most one hole, when all data points are present). This is done in `contour_ect()`

I store these in "ECT matrices" (3D np arrays) where each ECT[i,j] is an ECT with a different number of linearly spaced directions and resolution determined by i and j respectively. ECT matrix creation is handled by `compute_ect.py`.
Current indexing is as follows:

N_ANGLES = [2, 4, 8, 16, 32]\
RESOLUTIONS = [10, 20, 30, 40, 50]

example: ECT[3,4] gives the ECT with 16 linearly spaced directions on S1 and 50 linearly spaced heights over the leaf for each direction (resolution=50)

## Files 

Refer to this section if any data creation needs to be rerun or modified 

`compute_ect.py`

`contour_order.py`

`ect.py`

`ect_jobs.py`

`contour_jobs.py`
