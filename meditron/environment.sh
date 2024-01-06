# For finding tokens before git commit, use ack
sudo yum install epel-release
sudo yum install ack

# For working with github use gh CLI
conda install -c conda-forge gh

# For commands like "conda activate env"
source ~/anaconda3/etc/profile.d/conda.sh

# For logging in to Huggingface
pip install huggingface_hub[cli]