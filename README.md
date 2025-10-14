# Intersight AI Bridge

**Intersight AI Bridge** simplifies the initial installation and usage of Cisco UCS devices for AI workloads such as AI Pods.  

> **Note**: Starting from **Step 3**, these tools can also be used on any Linux system, even without Cisco UCS hardware.

This project provides scripts and configurations to:  
1. Deploy a **Server Profile** on Cisco Intersight.  
2. Install an **Operating System** through the Intersight OS Install feature (requires an *Advantage* license, otherwise can be done manually).  
3. Set up your environment for GPU-based AI workloads with three possible use cases:  
   - **Chatbot with VLLM + OpenWebUI**  
   - **Chatbot with Text Generation WebUI**  
   - **Chatbot with VLLM + Retrieval-Augmented Generation (RAG)**  


## Getting Started

### Step 1: Deploy the Server Profile
*Detailed instructions for deploying a Server Profile with a JSON provided config file on Cisco Intersight will be added here soon.*  
(Can be skipped if you prefer manual configuration or are not using Intersight.)


### Step 2: Install the Operating System through Intersight OS Install feature
*[Detailed instructions for Step 2](tutorials/README_Step_2.md)*

(Can be skipped if you prefer manual installation or are not using Intersight.)

### Step 3: Requirements Installation & Setup

1. Clone the repository (make sure to export the proxy if needed) and run the setup script:
   ```bash
   git clone https://github.com/mabuelgh/intersight-ai-bridge
   cd intersight-ai-bridge
   chmod +x *.sh
   ./setup.sh
   ```
   **Note**: This action will conclude with a reboot.
   
   The setup script will automatically add a Portainer container at *http://ipserver:9000* (this is optionnal and can be removed).

2. Verify installation:
   ```bash
   cd intersight-ai-bridge
   ./checking.sh
   ```
   This process will trigger the creation of a Docker container. It will then display your CPUs inside the container to confirm the Nvidia container toolkit installation.

## Use Case Scenarios

After setup, choose one of the following scenarios:

### 1. Chatbot: VLLM + OpenWebUI
Launch VLLM with OpenWebUI:  
```bash
./scenario1.sh
```
**Note**: If not done automatically, select your model on the top left corner of OpenWebUI.

### 2. Chatbot: Text Generation WebUI
Launch with the Text Generation WebUI project:  
```bash
./scenario2.sh
```
**Note**: You may need to load your model in the settings page before using it.


### 3. Chatbot: VLLM + RAG (File Context)
Launch VLLM with RAG for file-based context:  
```bash
./scenario3.sh
```
**Note**: This project comes with sample files about fictives company descriptions.

#### 📖 Sample of questions to ask based on the RAG files in the project
Once running, you can ask questions such as:
- *"When was Chronos Innovations created?"*  
- *"What's the business of Nimbus Orchard?"*  
- *"What is LuminaTech Solutions?"*  

## Notes
- Monitor GPUs with commands: "**nvidia-smi**" & "**nvtop**"
- Steps 1 and 2 are optional if you’re not using Cisco Intersight  
- Scripts are modular, feel free to adapt them for your environment
- Tested with ubuntu-22.04.2-live-server on Cisco UCSX-210C-M7 with NVIDIA L40S GPU

## Features and improvements to come
- Complete Step 1 Instructions
- Put scenario 3 python utilisation inside a container instead of on the OS directly
- Create a scenario 4 to showcase GPU activity

## Authors

* **Adrien Lécharny** - *Creator* - [GitHub account link](https://github.com/alecharn)
* **Marc Abu El Ghait** - *Initial work* - [GitHub account link](https://github.com/mabuelgh)
