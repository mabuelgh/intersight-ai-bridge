# Intersight AI Bridge — Cisco Stack Automation Blueprints

This folder contains **Quali Torque blueprints** that integrate Intersight AI Bridge into [**Cisco Stack Automation by Quali**](https://stackautomation.cisco.com/).  
Each blueprint automates one step of the end-to-end AI infrastructure deployment pipeline and can be used **independently or as part of a full workflow**.

> [!NOTE]
> These blueprints are designed to run on a Quali Torque agent with access to the target network. Make sure a Torque agent is deployed and reachable before launching any blueprint.

---

## Overview

| Blueprint | Step | Description |
|-----------|------|-------------|
| `ai_bridge_step1.yaml` | Step 1 | Deploy Server Profile on Intersight |
| `ai_bridge_step2.yaml` | Step 2 | OS Install only (Intersight OS Install feature) |
| `ai_bridge_step3.yaml` | Step 3 | Environment setup on Ubuntu (Docker, NVIDIA toolkit, etc.) |
| `ai_bridge_step4.yaml` | Step 4 | Deploy AI workload use case scenario |
| `ai_bridge_all_steps.yaml` | Step 1, 2, 3 & 4 | Deploy AI workload from empty server to deployed LLM |

> [!TIP]
> Each blueprint can be launched independently. If you already completed a step manually, skip to the next one.

---

## Prerequisites

- A running **Quali Torque** environment with Cisco Stack Automation
- A Torque **agent** deployed in the target environment with network access to the server and Intersight
- An **Intersight API key** (Key ID + EC Private Key) — see [Step 1 documentation](../intersight/tutorials/Step_1.md)
- The asset **`qualy_samples`** configured as a Torque repository asset, pointing to this repository (used to provide helper scripts to the agent)
- Intersight **Advantage license** for OS Install features (Steps 1 & 2); can be skipped for manual installs

---

## How to use it

- Log on to https://stackautomation.cisco.com/ with a Cisco ID
- Follow the "Journey" steps to install a Stack Automation server agent in your infrastructure
- Click on Automation and Repositories
- Select Add Repository, select GitHub
- Enter the URL https://github.com/mabuelgh/intersight-ai-bridge
- Create a Credential Set with a GitHub personal token
- Click on Connect
- Once linked, click on Assets, select the Blueprint you want to use (either the full steps or individual steps) with the Launch icon
- Select the name of the deployment and the duration (Always On is recommended for this deployment)
- Set all the Environment values and the previously installed agent
- Launch the deployment

> [!TIP]
> You might need to switch the active Space from "All Spaces" to a specific one.

---

## Common Inputs

All blueprints share a common set of inputs. Defaults are provided as examples and **must be replaced** with your environment values.

| Input | Description | Example |
|-------|-------------|---------|
| `agent` | Torque agent to execute the blueprint on | *(agent selector)* |
| `PROXY_URL` | HTTP/HTTPS proxy URL (leave blank if not needed) | `http://proxy.example.com:80` |
| `INTERSIGHT_API_KEY_ID` | Intersight API Key ID | `671235.../...` |
| `INTERSIGHT_PRIVATE_KEY` | EC Private Key for Intersight API (single-line, spaces between header and body) | `-----BEGIN EC PRIVATE KEY----- ... -----END EC PRIVATE KEY-----` |
| `INTERSIGHT_HOST` | Intersight endpoint URL | `https://eu-central-1.intersight.com` |
| `SERVER_SERIAL` | Serial number of the target UCS server | `FCH290475TC` |
| `SERVER_NAME` | Logical name of the server in Intersight | `CSS-DCC7-1-6` |
| `SERVER_PROFILE_NAME` | Name of the server profile to create/assign | `IAIB-AI-IMM-1` |
| `NATIVE_VLAN_ID` | Native VLAN ID for the server NIC policy | `541` |
| `ALLOWED_VLANS` | Allowed VLANs on the trunk | `541` |
| `INBAND_VLAN_ID` | In-band management VLAN ID | `541` |
| `MGMT_IP_FROM` / `MGMT_IP_TO` | IP pool range for in-band management | `10.48.54.95` |
| `MGMT_GATEWAY` | Gateway for management network | `10.48.54.1` |
| `MGMT_PRIMARY_DNS` / `MGMT_SECONDARY_DNS` | DNS servers for management network | `10.60.1.1` / `10.60.1.2` |
| `POLICIES_PREFIX` | Prefix used when naming Intersight policies | `Q-IAIB` |
| `ORGANIZATION_NAME` | Intersight organization name | `default` |
| `OS_IMAGE_NAME` | OS ISO image name as registered in Intersight | `ubuntu-24.04.3-live-server-amd64.iso` |
| `SCU_IMAGE_NAME` | SCU image name as registered in Intersight | `SCU-7.1.5.250100` |
| `SERVER_IP_ADDRESS` | Target OS IP address with prefix length | `10.48.54.85/25` |
| `SERVER_GATEWAY` | OS-level default gateway | `10.48.54.1` |
| `SERVER_INTERFACE` | NIC interface name on the OS | `eno5` |
| `SERVER_HOSTNAME` | Hostname to assign to the server | `ai-server-q` |
| `SERVER_TIMEZONE` | Timezone for the OS | `UTC` |
| `PRIMARY_DNS` / `SECONDARY_DNS` | DNS servers for the OS | `10.60.1.1` / `8.8.8.8` |

> [!CAUTION]
> The `INTERSIGHT_PRIVATE_KEY` input is sensitive. It will be visible in the deployment logs. It is highly recommended to deactivate this API key once the deployment is over, or to delete the deployment from Stack Automation.

---

## Blueprint Details

### `step1.yaml` — Deploy Server Profile + OS Install

Generates the Intersight configuration from template variables, pushes it via EasyUCS, and deploys the server profile using `deploy_server_profile.py`. It then waits for the task to complete.


*Use this blueprint when starting from scratch with a bare-metal UCS server.*

---

### `step2.yaml` — OS Install Only

Runs only the OS Install grain (Step 2). Useful if the server profile was already deployed manually or in a previous run.

Calls `os_install.py` with the configured Intersight credentials and server parameters, then waits for the task to complete via `wait_for_finish_task.py`.

---

### `step3.yaml` — Environment Setup (Ubuntu)

SSHes into the server at `SERVER_IP_ADDRESS` and runs the environment setup remotely:
- Installs system dependencies
- Configures proxy settings if needed
- Installs Docker and NVIDIA Container Toolkit
- Prepares the server for AI workload deployment

> [!IMPORTANT]
> The SSH credentials for the server are currently hardcoded in the blueprint. This will be replaced by a dedicated input variable in a future version.

> [!NOTE]
> This step is equivalent to running `./setup.sh` manually on the server. See [Step 3 documentation](../intersight/tutorials/Linux_Step_2.md) for details.

---

### `step4.yaml` — AI Workload Deployment

SSHes into the server and launches the selected AI use case scenario.

**Additional input specific to this blueprint:**

| Input | Description | Default |
|-------|-------------|---------|
| `USE_CASE_SCENARIO` | Scenario number to launch (`1`, `2`, `3`, `4`) | `3` |

Scenario mapping:

| Value | Scenario |
|-------|----------|
| `1` | Chatbot — Text Generation WebUI |
| `2` | Chatbot — vLLM + OpenWebUI |
| `3` | Chatbot — vLLM + RAG (File Context) |
| `4` | GPU Stresstest — vLLM with curl containers |

> [!NOTE]
> Depending on network speed and model download size, this step may take a long time. Consider increasing the Torque blueprint timeout above the default **2 hours** if needed.

---

## Torque Asset Configuration

The blueprints reference a Torque asset to inject the `wait_for_finish_task.py` helper script into the agent environment.  

```yaml
files:
  - source: intersight-ai-bridge
    path: scripts/wait_for_finish_task.py
```

> [!TIP]
> The `wait_for_finish_task.py` script is located at [`scripts/wait_for_finish_task.py`](../scripts/wait_for_finish_task.py) in this repository.

---

## Notes

- All blueprints use `spec_version: 2` (Quali Torque shell grain format)
- Proxy injection is handled automatically: if `PROXY_URL` is set to a non-placeholder value, it is injected into the relevant Python scripts at runtime
- Tested with Cisco UCSX-210C-M7 with 2 x NVIDIA L40S GPU, Ubuntu 24.04.3

---

## Coming Soon

- Integration with Intersight Resource integration inside Stack Automation
- Full end-to-end automated run
- Secured way to use the API Secret Key
- Non-hardcoded SSH credentials for the server
- Compatibility with OCP deployment
