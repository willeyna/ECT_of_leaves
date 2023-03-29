import os
import sys
import ect
import numpy as np

# choose in this file the specifics of the ECT matrices
N_ANGLES = [2, 4, 8, 16, 32]
RESOLUTIONS = [10, 20, 30, 40, 50]

dir_path = str(sys.argv[1])
# remove ./data/ and Scalexy from path to set up dir with same structure as data dir to store output data
boneless_path = '/'.join(dir_path.split('/')[2:])
output_path = os.path.join('./leaf_ect', boneless_path)

if not os.path.exists(output_path):
   os.makedirs(output_path)

for file in os.listdir(dir_path):
    file_path = os.path.join(dir_path, file)

    leaf = np.load(file_path)
    E = ect.ect_matrix(leaf, N_ANGLES, RESOLUTIONS)

    # [:-4] gets rid of the .txt in filename
    np.save(os.path.join(output_path, file[:-4]), E)
