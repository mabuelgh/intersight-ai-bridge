### Step 3: Requirements Installation & Setup
**Please follow guidelines from Step 2 before continuing to Step 3**

**Note**: We will assume in the following command lines that the cluster name is **"CLUSTER_NAME"** or **"BASE_DOMAIN"** and your OCP IP is **"DESIRED_OS_IP_ADDRESS"**, please replace it with the value of CLUSTER_NAME, BASE_DOMAIN and DESIRED_OS_IP_ADDRESS in .env

## Setup Deployment

1. We will now install all the operators needed to make our platform work perfectly:
   ```bash
   # pwd 
   # > ai-bridge/OCP/iserver
   cp ../operators.json ./
   # We need to setup all the remaining info related to our cluster
   DESIRED_IP=$(grep "^DESIRED_OS_IP_ADDRESS=" ../.env | cut -d'=' -f2 | tr -d "'")
   cp $HOME/.itool/ocp-clusters/CLUSTER_NAME/kubeconfig ./
   cp ../ssh.pub ./
   python iserver.py set ocp connector --cluster CLUSTER_NAME --kubeconfig ./kubeconfig  --mgmt $DESIRED_IP --ssh ./ssh.pub
   # Now configuring all the operators needed
   python iserver.py set ocp task --cluster CLUSTER_NAME --filename $PWD/operators.json  --no-confirm
   ```

2. We will send the Kubeconfig and other config files to OCP and then connect to it:
   ```bash
   cd ..
   cp $HOME/.itool/ocp-clusters/CLUSTER_NAME/kubeconfig ./
   scp -i ssh ./kubeconfig core@DESIRED_OS_IP_ADDRESS:./
   scp -i ssh ./configs/* core@DESIRED_OS_IP_ADDRESS:./
   ssh -i ssh core@DESIRED_OS_IP_ADDRESS
   ```
   From now on the provided commands will need to be send directly when connected to OpenShift on SSH:
   ```bash
   mkdir configs
   mv *.yaml ./configs
   mkdir ocp
   cd ocp
   mkdir auth
   cd auth
   mv ../../kubeconfig ./
   mkdir ~/.kube
   cp kubeconfig ~/.kube/config
   cd
   ```
   The operations above will let you push configurations from the CLI:
   ```bash
   oc apply -f configs/init.yaml
   ````

3. We can now start configuring OpenShift with the help of the **installed operators**:
   ### Node Feature Discovery
      ```bash
      oc apply -f configs/nfd.yaml
      ```
      CLI commands to check:
      ```bash
      oc get pods -n openshift-nfd
      oc describe node | egrep 'Roles|pci' 
      ```
      Look for "pci-10de" which means a nvidia GPU was discovered

   ### NVIDIA GPU - Cluster Policy
      ```bash
      oc apply -f configs/nvidia.yaml
      ```
      CLI commands to check:
      ```bash
      oc get pod -n nvidia-gpu-operator
      # Wait for the pod nvidia-driver-deamonset-xx and nvidia-container-toolkit-daemonset-xx to be "Running"
      # Might takes a bit of time as the pod will pull images from nvcr.io
      oc exec daemonset/nvidia-device-plugin-daemonset -n nvidia-gpu-operator -- nvidia-smi
      ```
      **Notes**: 
      - Wait for all the pods to have status "Running" or "Completed"
      - The **SMI** commands is a good way to know if the GPU are detected and working but also checking what's running on the GPU and there utilisation.

   ### (Optionnal) Split each GPU to 2 vGPU
      ```bash
      oc apply -f configs/gputimeslicing.yaml 
      oc patch clusterpolicy gpu-cluster-policy -n nvidia-gpu-operator --type merge -p '{"spec": {"devicePlugin": {"config": {"name": "time-slicing-config", "default": "any"}}}}'
      ```
      CLI commands to check:
      ```bash
      oc get node --selector=nvidia.com/gpu.product -o json | jq '.items[0].status.capacity'
      # Look for the number of GPU available in "nvidia.com/gpu" field
      ```
      Revert:
      ```bash
      oc patch clusterpolicy gpu-cluster-policy -n nvidia-gpu-operator --type merge -p '{"spec": {"devicePlugin": {"config": {"name": "", "default": ""}}}}'
      ```

   ### Local Storage
      ```bash
      sudo wipefs -a /dev/nvme1n1
      oc apply -f configs/localstorage.yaml
      oc patch storageclass local-nvme -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
      ```

   ### NVIDIA NIM - Cache
      You'll need an NVIDIA account on *[ngc.nvidia.com](ngc.nvidia.com)* for this section. 

      Select *Setup*, click on *Generate API Key*, use *Key Value* starting with "nvapi" and replace **NVAPI_YOUR_API_KEY** with it.
      ```bash
      oc create configmap nim-empty-ca-configmap -n openshift-operators --from-literal=dummy-key=dummy-value
      export NGC_API_KEY=NVAPI_YOUR_API_KEY
      oc create secret docker-registry ngc-secret --docker-server=nvcr.io --docker-username='$oauthtoken' --docker-password=$NGC_API_KEY -n openshift-operators
      oc create secret docker-registry regcred --docker-server=nvcr.io --docker-username='$oauthtoken' --docker-password=$NGC_API_KEY -n openshift-operators
      oc create secret generic ngc-api-secret --from-literal=NGC_API_KEY=$NGC_API_KEY -n openshift-operators
      ```

      You need to **change the proxy**, and noproxy *before* using the nimcache.yaml file:
      ```bash
      nano configs/nimcache.yaml
      oc apply -f configs/nimcache.yaml
      ```

      CLI commands to check:
      ```bash
      oc get pod -n openshift-operators
      # Step 1 : Wait for meta-llama3-1b-instruct-pod to be Running
      # Step 2 : Look for the instruct-job id with the command above and replace it below, monitor the completion of the pod
      oc logs meta-llama3-1b-instruct-job-ID -n openshift-operators
      ```
      **Notes**: 
      - This process can be very long as this will let the system download the LLM.
      - First a meta-llama3-1b-instruct-pod will appear, then terminate. Next, wait for meta-llama3-1b-instruct-job-xxx to start and be "Completed" before continuing.

   ### NVIDIA NIM - Service
      ```bash
      oc apply -f configs/nimservice.yaml 
      # create internal route
      oc expose svc/meta-llama3-1b-instruct -n openshift-operators
      ```

      CLI commands to check:
      ```bash
      oc get pod -n openshift-operators
      ```
      **Note**: Look for meta-llama3-1b-instruct-xxx the have the READY parameter at 1/1

