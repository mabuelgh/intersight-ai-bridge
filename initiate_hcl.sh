#!/bin/bash

# Description: This script installs the necessary tools for HCL enablement on host machine from https://github.com/cisco-intersight/os-discovery-tool-linux.git
# mabuelgh - Nov 2026

cd ..
sudo apt install -y ipmitool
DEB_URL=$(curl -s https://api.github.com/repos/cisco-intersight/os-discovery-tool-linux/releases/latest | grep -o '"browser_download_url": *"[^"]*\.deb"' | cut -d '"' -f4)
curl -L -o ucs-tool-latest.deb "$DEB_URL"
sudo dpkg -i ucs-tool-latest.deb