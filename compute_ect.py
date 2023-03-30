import os
import sys
import ect
import numpy as np

# choose in this file the specifics of the ECT matrices
N_ANGLES = [1]
RESOLUTIONS = [2]
# overall output path for all ect files
ect_output_path = './leaf_ect/'


# dont change under this ~~~~~
dir_path = str(sys.argv[1])
depth = int(sys.argv[2])

# remove ./data/ and Scalexy from path to set up dir with same structure as data dir to store output data
boneless_path = '/'.join(dir_path.split('/')[depth:])
output_path = os.path.join(ect_output_path, boneless_path)

if not os.path.exists(output_path):
   os.makedirs(output_path)

for file in os.listdir(dir_path):
    file_path = os.path.join(dir_path, file)

    leaf = np.load(file_path)
    E = ect.ect_matrix(leaf, N_ANGLES, RESOLUTIONS)

    # [:-4] gets rid of the .txt in filename
    np.save(os.path.join(output_path, file[:-4]), E)
