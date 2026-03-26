#!/bin/bash

# Description: This script runs a 3 containers : one for text generation, one for embeddings, and one for open-webui. Then execute a script to deploy RAG file context.
# mabuelgh - Mar 2026

# Variables
LLM_MODEL="mistralai/Ministral-3-14B-Instruct-2512"
LLM_EMBEDDING_MODEL="BAAI/bge-base-en-v1.5" # Alternative embedding model, to test
LLM_MODEL_FOLDER="${LLM_MODEL#*/}"
LLM_EMBEDDING_MODEL_FOLDER="${LLM_EMBEDDING_MODEL#*/}"
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

print_subsection_header "Downloading LLM model: $LLM_EMBEDDING_MODEL"
sudo hf download $LLM_EMBEDDING_MODEL --local-dir ./models/$LLM_EMBEDDING_MODEL_FOLDER

# Part 2: Set up Docker containers
print_section_header "Setup Docker Containers"
IP_ADDRESS=$(ip -4 addr show $INTERFACE | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
if sudo docker compose -f docker-compose-vllm-RAG.yml up -d; then
    echo "Docker image built successfully and container running successfully."
    print_subsection_header "When the model are deployed, press enter to continue and initiate chat with RAG context in Open WebUI."
    read -r
    # We need to make this curl operation to initiate the creation of a "no auth" user first, then we can execute the rag.sh script to create the knowledge base and upload files, which requires the token from a real user.
    curl -H "Content-Type: application/json" -d '{"email":"","password":""}' http://127.0.0.1:3001/api/v1/auths/signin > /dev/null 2>&1    
    ./initiate_rag.sh
    print_subsection_header "Access the web interface at http://$IP_ADDRESS:3001"
else
    echo "Failed to build Docker image or to run Docker container."
    exit 1
fi