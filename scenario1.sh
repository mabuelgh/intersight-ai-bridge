#!/bin/bash

# Description: This script runs a text-generation-webui container with Nvidia GPU support and downloads an LLM model to be used by the container.
# alecharn - Nov 2024
# mabuelgh - Sep 2025

# Variables
LLM_MODEL="microsoft/Phi-3-mini-4k-instruct-gguf"
# LLM_MODEL="microsoft/Phi-4-mini-instruct"
LLM_MODEL_FOLDER="${LLM_MODEL#*/}"
# INTERFACE="ens33" # For UCS-C server
INTERFACE="eno5" # For UCS-X compute node

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

# Part 1: Download text-generation-webui-docker from github
print_section_header "Pulling the GitHub repository for text-generation-webui-docker"
sudo git clone https://github.com/Atinoda/text-generation-webui-docker

print_subsection_header "Copying docker-compose-text-generation-webui.yml to text-generation-webui-docker"
sudo cp ./docker-compose-text-generation-webui.yml text-generation-webui-docker/

# Part 2: Download model(s) from huggingface
print_section_header "Downloading model(s) from Hugging Face"

print_subsection_header "Downloading LLM model: $LLM_MODEL"
sudo hf download $LLM_MODEL --local-dir ./models/$LLM_MODEL_FOLDER

# Part 3: Build and run text-generation-webui docker container
print_section_header "Building and running text-generation-webui docker container"
IP_ADDRESS=$(ip -4 addr show $INTERFACE | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
cd ./text-generation-webui-docker
if sudo docker compose -f docker-compose-text-generation-webui.yml up -d; then
    echo "Docker image built successfully and container running successfully."
    print_subsection_header "Access the web interface at http://$IP_ADDRESS:7860 (might take a moment to become available)"
    # Necessary for models such as Phi-3-mini-4k-instruct
    sudo docker exec text-generation-webui pip uninstall -y flash-attn 
else
    echo "Failed to build Docker image or to run Docker container."
    exit 1
fi