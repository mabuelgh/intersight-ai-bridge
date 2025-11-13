#!/bin/bash

# Description: This script runs a text-generation-webui container with Nvidia GPU support and downloads an LLM model to be used by the container.
# alecharn - Nov 2024
# mabuelgh - Sep 2025

# Variables
# LLM_MODEL="microsoft/Phi-3-mini-4k-instruct-gguf"
LLM_MODEL="microsoft/Phi-4-mini-instruct"
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

# Part 1: Download model(s) from huggingface
print_section_header "Downloading model(s) from Hugging Face"

print_subsection_header "Downloading LLM model: $LLM_MODEL"
sudo hf download $LLM_MODEL --local-dir ./models/$LLM_MODEL_FOLDER

# Part 2: Build and run vLLM and Open-WebUI dockers containers
print_section_header "Building and running vLLM and Open-WebUI docker containers"
IP_ADDRESS=$(ip -4 addr show $INTERFACE | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
if sudo docker compose -f docker-compose-vllm.yml up -d; then
    echo "Docker image built successfully and container running successfully."
    print_subsection_header "Access the web interface at http://$IP_ADDRESS:3000 (might take a few moments to become available)"
else
    echo "Failed to build Docker image or to run Docker container."
    exit 1
fi