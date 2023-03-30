import os
import sys
import ect
import numpy as np

# path to leaf_data. assumes original file structure of leaf data dir
data_dir = '/mnt/research/morphology_lab/Data/leaf_data/'

depth = len(data_dir.split("/"))-1
for root, dirs, files in os.walk(data_dir):
    if 'Scale' in root:
        print("Working on:", root)
        # remove ./data/ and Scalexy from path to set up dir with same structure as data dir to store output data
        boneless_path = '/'.join(root.split('/')[depth:-1])
        output_path = os.path.join('./contour_data', boneless_path)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        for file in os.listdir(root):
            file_path = os.path.join(root, file)
            error = False

            leaf = np.loadtxt(file_path, delimiter = ',')

            # if starts and ends at same point, assume leaf is good to go
            if np.all((leaf[0] - leaf[-1]) == 0):
                leaf_contour = leaf
            else:
                # in many cases 2NN graph will be unable to find a contour walk; we do not include the leaf in this case
                try:
                    leaf_contour = ect.contour_order(leaf)
            
                    # catches leaves who can make a contour but one that can't even cover half of the data points
                    if leaf_contour is None:
                        error = True

                # if no path, ignore, else just 
                except Exception as e:
                    error = True

                    if "No path between" in str(e):
                        pass
                    else:
                        print(e)
                        break

            if not error:
                np.save(os.path.join(output_path, file[:-4]), leaf_contour) 
