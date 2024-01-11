# For finding tokens before git commit, use ack
sudo yum install epel-release
sudo yum install ack

# For working with github use gh CLI
type -p yum-config-manager >/dev/null || sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
sudo yum install -y gh

# For commands like "conda activate env"
echo 'source ~/anaconda3/etc/profile.d/conda.sh' >> ~/.profile
source ~/anaconda3/etc/profile.d/conda.sh

# Install the required packages in the pytorch environment since that is
# the preferred module over tensorflow
conda activate pytorch_p310
pip install -r requirements.txt
huggingface-cli login

# Create a separate environment for fastchat and its dependencies (Optional)
conda create --clone pytorch_p310 --name fastchat
pip install -r requirements.txt