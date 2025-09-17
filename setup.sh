#!/bin/bash

# Description: This script installs the necessary tools and configurations to make a guest machine AI-ready.
# alecharn - Nov 2024
# mabuelgh - Sep 2025

# Variables
PROXY_URL="http://your.new.proxy:80"

# Part 0: Functions to create section and subsection headers
print_section_header() {
    local section_title=$1
    echo ""
    echo "#----------------------------------------------------------------#"
    echo "# $section_title"
    echo "#----------------------------------------------------------------#"
    echo ""
}

print_subsection_header() {
    local subsection_title=$1
    echo ""
    echo "## $subsection_title"
    echo ""
}

# Part 1: Append Cisco proxy settings to host environment
print_section_header "Appending Cisco proxy settings to host environment"
echo "HTTP_PROXY=$PROXY_URL
HTTPS_PROXY=$PROXY_URL
http_proxy=$PROXY_URL
https_proxy=$PROXY_URL
FTP_PROXY=${PROXY_URL}/
NO_PROXY=localhost,127.0.0.1,171.*,172.*,192.*,10.*,1.*" | sudo tee -a /etc/environment

# Part 2: Update the package list
print_section_header "Updating the package list"
sudo apt-get update
# sudo apt upgrade -y

# Part 3: Docker Installation
print_section_header "Installing Docker"

print_subsection_header "Adding Docker's official GPG key"
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

print_subsection_header "Adding the Docker repository to Apt sources and updating the package list"
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

print_subsection_header "Installing Docker packages"
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

print_subsection_header "Appending Cisco proxy settings to Docker service configuration"
sudo mkdir -p /etc/systemd/system/docker.service.d
echo "[Service]
Environment=\"HTTP_PROXY=$PROXY_URL\"
Environment=\"HTTPS_PROXY=$PROXY_URL\"
Environment=\"http_proxy=$PROXY_URL\"
Environment=\"https_proxy=$PROXY_URL\"
Environment=\"NO_PROXY=localhost,127.0.0.1,*.cisco.com,171.*,172.*,192.*,10.*,1.*\"" | sudo tee -a /etc/systemd/system/docker.service.d/http-proxy.conf

print_subsection_header "Reloading the Docker daemon"
sudo systemctl daemon-reload
sudo systemctl restart docker

# Part 3-bis : Install Portainer (Optional)
print_section_header "Installing Portainer"
sudo docker run -d -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
print_section_header "Access the Portainer web interface at http://localhost:9000"

# Part 4: Install Nvidia Drivers
print_section_header "Installing Nvidia Drivers"
sudo ubuntu-drivers autoinstall

# Part 5: Install Nvidia container toolkit
print_section_header "Installing Nvidia container toolkit"

print_subsection_header "Adding Nvidia's official GPG key"
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# print_subsection_header "Configuring the repository to use experimental packages"
# sudo sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list

print_subsection_header "Updating the package list"
sudo apt-get update

print_subsection_header "Installing Nvidia container toolkit"
sudo apt-get install -y nvidia-container-toolkit

print_subsection_header "Configuring Docker container runtime to use Nvidia GPU"
sudo nvidia-ctk runtime configure --runtime=docker

print_subsection_header "Reloading the Docker daemon"
sudo systemctl restart docker

print_subsection_header "Configuring Nvidia / Docker runtime in rootless mode"
sudo nvidia-ctk runtime configure --runtime=docker --config=$HOME/.config/docker/daemon.json
sudo systemctl --user restart docker
sudo sudo nvidia-ctk config --set nvidia-container-cli.no-cgroups --in-place

# Part 5bis: Install Nvidia CUDA Toolkit
# print_section_header "Installing Nvidia CUDA Toolkit"
# sudo apt-get install -y nvidia-cuda-toolkit

# Part 6: Install Dev tools and AI tools 
print_section_header "Installing AI tools"

print_subsection_header "Installing Python3 and pip"
sudo apt-get install -y python3 python3-pip

print_subsection_header "Installing htop tool to monitor CPU usage"
sudo apt-get install htop

print_subsection_header "Installing nvtop tool to monitor GPU usage"
sudo apt-get install nvtop

print_subsection_header "Installing huggingface hub"
sudo pip install huggingface_hub

# Part 7: Reboot host machine
print_section_header "All done! Rebooting now..."
sudo reboot 