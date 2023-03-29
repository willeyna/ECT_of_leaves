import os

def write_sb(dir_name, name, hrs, mem):
    contents = f"""#!/bin/bash --login
########## SBATCH Lines for Resource Request ##########

#SBATCH --time={hrs}:00:00
#SBATCH --mem={mem}G
#SBATCH --job-name {name}_ect
#SBATCH --output /mnt/research/IceCube/willey/ECT_of_leaves/outputs/{name}_ect.out

########## Command Lines to Run ##########
cd /mnt/research/IceCube/willey/ECT_of_leaves/
export PATH=$PATH:/mnt/research/IceCube/willey/conda3/bin/
conda activate base
/mnt/research/IceCube/willey/conda3/bin/python3 /mnt/research/IceCube/willey/ECT_of_leaves/compute_ect.py {dir_name}"""

    return contents

# 24hrs should be enough!! 48 to be very safe; max 10k files in a single directory
hrs = str(input("How many hours per job?"))
mem = str(input("How many GB of memory per job?"))

sb_filenames = []

data_dir = './contour_data/'
sb_dir = './submit/'


# loop through directories and create sb files in submit dir
for root, dirs, files in os.walk(data_dir):
    # fix to ignore hidden files (git, ds_store, etc)
    cleaned_files = [f for f in files if not f[0] == '.']
    # choosing to use scaled xy coords
    if cleaned_files and 'Nonscale' not in root:
        name = '_'.join(root.split('/')[2:])
        sb_filenames.append(name+'.sb')

        # write sb for each directory of data files
        sb_contents = write_sb(root, name, hrs, mem)
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
