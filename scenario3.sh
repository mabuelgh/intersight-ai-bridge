#!/bin/bash

# Description: This script runs a 3 containers : one for text generation, one for embeddings, and one for open-webui. Then execute a python script to use the RAG file context.
# mabuelgh - Sep 2025

# Variables
LLM_MODEL="microsoft/Phi-4-mini-instruct"
LLM_EMBEDDING_MODEL="Qwen/Qwen3-Embedding-0.6B"
LLM_MODEL_FOLDER="${LLM_MODEL#*/}"
LLM_EMBEDDING_MODEL_FOLDER="${LLM_EMBEDDING_MODEL#*/}"


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

print_subsection_header "Downloading LLM model: $LLM_EMBEDDING_MODEL"
sudo hf download $LLM_EMBEDDING_MODEL --local-dir ./models/$LLM_EMBEDDING_MODEL_FOLDER

# Part 2: Set up Docker containers
print_section_header "Setup Docker Containers"
if sudo docker compose -f docker-compose-vllm-RAG.yml up -d; then
    pip install --break-system-packages -r python_rag_requirements.txt
    echo "Docker image built successfully and container running successfully."
    print_subsection_header "It might take a few moments to be available, when finished press enter to initiate chat with RAG context."
    read -r
    python3 retrieval_augmented_generation_with_langchain.py --directory-path ./rag-files/
else
    echo "Failed to build Docker image or to run Docker container."
    exit 1
fi