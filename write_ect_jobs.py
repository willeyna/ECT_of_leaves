import os
# changing directory structure probably breaks things :)  
# where to read input data from 
data_dir = '/mnt/research/IceCube/willey/ECT_of_leaves/hiding/contour_data/'
# where to store ect data
output_dir = './leaf_ect/'
# where to put sb files for submission 
sb_dir = './submit/'

# hrs and memory for each job
hrs = '24'
mem = '8'

def write_sb(input_dir, depth, name, hrs, mem):
    contents = f"""#!/bin/bash --login
########## SBATCH Lines for Resource Request ##########
#SBATCH --time={hrs}:00:00
#SBATCH --mem={mem}G
#SBATCH --job-name {name}_ect
#SBATCH --output /mnt/research/morphology_lab/Code/ECT_of_leaves/outputs/{name}_ect.out
########## Command Lines to Run ##########
cd /mnt/research/morphology_lab/Code/ECT_of_leaves/

python compute_ect.py {input_dir} {depth}"""
    return contents

# annoying variable for file naming purposes
depth = len(data_dir.split('/'))-1

sb_filenames = []
# loop through directories and create sb files in submit dir
for root, dirs, files in os.walk(data_dir):
    # fix to ignore hidden files (git, ds_store, etc)
    cleaned_files = [f for f in files if not f[0] == '.']
    # choosing to use scaled xy coords
    if cleaned_files and 'Nonscale' not in root:
        name = '_'.join(root.split('/')[depth:])
        sb_filenames.append(name+'.sb')
        
        # write sb for each directory of data files
        sb_contents = write_sb(root, depth, name, hrs, mem)
        fout=open(os.path.join(sb_dir, name + '.sb'), "w")
        fout.write(sb_contents)
        fout.close()

# create bash file to run every sb file
bash_contents = "#!/bin/bash\n"
for file in sb_filenames:
    bash_contents += ("sbatch " + file + "\n")

fout=open(os.path.join(sb_dir, 'run.sh'), "w")
fout.write(bash_contents)
fout.close()
