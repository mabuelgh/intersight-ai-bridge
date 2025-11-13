#!/bin/bash

# Description: This script verifies the installation of Docker, Nvidia drivers, and Nvidia container toolkit on a host machine.
# alecharn - Nov 2024

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

# Part 1: Run hello-world container to verify Docker installation
print_section_header "Running hello-world container to verify Docker installation"
if sudo docker run hello-world; then
    print_subsection_header "Docker is installed and is running successfully."
else
    print_subsection_header "Failed to run Docker hello-world container."
    exit 1
fi

# Part 2: Run nvidia-smi to verify Nvidia drivers installation
print_section_header "Running nvidia-smi to verify Nvidia drivers installation"
if sudo nvidia-smi; then
    print_subsection_header "Nvidia drivers installation is successfull."
else
    print_subsection_header "Failed to install Nvidia drivers."
    exit 1
fi

# Part 3: Run sample CUDA container to verify Nvidia container tookit installation
print_section_header "Running sample CUDA container to verify Nvidia container tookit installation"

if sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi; then
    print_subsection_header "Nvidia container tookit is installed and is running successfully."
elif [[ $? -ne 0 ]]; then
    print_subsection_header "Failed to install Nvidia container tookit : an error occurred."
    output=$(sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi 2>&1)
    # Check if the error is due to NVML error and modify nvidia-container-runtime configuration file
    if [[ $output == *"Failed to initialize NVML: Unknown Error"* ]]; then
        echo "Detected 'Failed to initialize NVML: Unknown Error'"
        print_subsection_header "Modifying nvidia-container-runtime configuration file to set the parameter no-cgroups = false."
        sudo sed -i 's/no-cgroups = true/no-cgroups = false/' "/etc/nvidia-container-runtime/config.toml"
        if sudo sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi; then
            print_subsection_header "Nvidia container tookit is now running successfully!"
        else
            print_subsection_header "Failed to install Nvidia container tookit : an unexpected error occurred."
            exit 1
        fi
    else
        print_subsection_header "Failed to install Nvidia container tookit : an unexpected error occurred."
        exit 1
    fi
fi 