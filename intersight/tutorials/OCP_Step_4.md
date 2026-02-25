### Step 4: 

**Note**: We will assume in the following command lines that the cluster name is **"CLUSTER_NAME"** or **"BASE_DOMAIN"** and your OCP IP is **"DESIRED_OS_IP_ADDRESS"**, please replace it with the value of CLUSTER_NAME, BASE_DOMAIN and DESIRED_OS_IP_ADDRESS in .env

## Use Case Scenarios

After setup, choose one of the following scenarios:

### 1. ChatBot : CURL
This POST will answer using the LLM installed using NIM Service:
```bash
curl -s -X POST http://meta-llama3-1b-instruct-openshift-operators.apps.CLUSTER_NAME.BASE_DOMAIN/v1/completions -H "Content-Type: application/json" \
  -d '{
    "model": "meta/llama-3.2-1b-instruct",
    "prompt": "Hello! Write a short haiku about OpenShift.",
    "max_tokens": 100
  }' | jq
```
**Notes**: 
- Don't forget to modify CLUSTER_NAME and BASE_DOMAIN based on your *.env* values.
- You can modify the prompt to your need.



### 2. ChatBot : Jupyter Playbook
```bash
oc apply -n openshift-operators -f configs/jupyter.yaml
oc expose svc/tensorflow-jupyter-notebook -n openshift-operators
```
**Notes**: 
- Use the [ai-pod-validation.ipynb](OCP/ai-pod-validation.ipynb) file to test easily your LLM through Jupyter Playbook
- Access Jupyter with http://tensorflow-jupyter-notebook-nvidia-gpu-operator.apps.CLUSTER_NAME.BASE_DOMAIN/
- Don't forget to modify CLUSTER_NAME and BASE_DOMAIN based on your *.env* values in both the above line and inside the Playbook
- First installation can be long due to the download of tensorflow LLM

### 3. GPU Burner
```bash
oc apply -n nvidia-gpu-operator -f configs/burn.yaml
```
**Note**: This process only last for 60 secondes. You can setup a long timeline if needed.


### 4. RedHat OpenShift AI : Jupyter Playbook
```bash
# pwd 
# > ai-bridge/OCP/iserver
cp ../operators_rhai.json ./
python iserver.py set ocp task --cluster CLUSTER_NAME --filename $PWD/operators_rhai.json  --no-confirm
```
**Notes**: 
- Once RedHat OpenShift AI installed, open https://rhods-dashboard-redhat-ods-applications.apps.CLUSTER_NAME.BASE_DOMAIN
- Go to Applications > Enabled > Start basic Workbench > Open Application
- Select the Workbench image needed, you can select "Jupyter | PyTorch | CUDA | Python"
- Once the workbench deployed, you can open Jupyter
- Use the [ai-pod-validation.ipynb](OCP/ai-pod-validation.ipynb) file to test easily your LLM through Jupyter Playbook


## Monitoring
- Monitor GPUs with SMI command: 
   ```bash
   oc get pod -n nvidia-gpu-operator
   # Look for the deamonset id with the command above and replace it below
   oc exec nvidia-driver-daemonset-ID -n nvidia-gpu-operator  -- nvidia-smi
   ```
- Monitor GPUs with Web UI : Observe > Dashboard > NVIDIA DCGM Exporter Dashboard:
   ```bash
   python iserver.py set ocp task --cluster CLUSTER_NAME --filename $PWD/gpu_dashboard.json  --no-confirm
   ```
- **Intersight has native visibility over the GPU activity**, without OS Agent. You can monitor GPU metrics directly from Intersight server inventory or through the Metrics Explorer