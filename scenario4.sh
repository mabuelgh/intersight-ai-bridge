#!/bin/bash

# Description: This script runs a 4 containers : two for text generation, two for POST curl to vLLM API.
# mabuelgh - Oct 2025

# Variables
LLM_MODEL="microsoft/Phi-4-mini-instruct"
LLM_MODEL_FOLDER="${LLM_MODEL#*/}"


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

# Part 2: Set up Docker containers
print_section_header "Setup Docker Containers"
if sudo docker compose -f docker-compose-vllm-stresstest.yml up -d; then
    echo "Docker image built successfully and container running successfully."
    print_subsection_header "It might take a few moments to be available. Check the logs with: sudo docker logs -f <container_id>"
else
    echo "Failed to build Docker image or to run Docker container."
    exit 1
fi