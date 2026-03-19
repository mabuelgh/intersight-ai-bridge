### Step 2: OCP Deployment

## Deployment

1. Clone this repository, navigate into the project directory:
   ```bash
   # git clone https://github.com/mabuelgh/intersight-ai-bridge.git # if not already done for step 1
   cd intersight-ai-bridge/OCP
   git clone https://github.com/datacenter/iserver.git
   ```

2. Set the environnement variables:
   Copy the env file and put your own values for your deployment
   ```bash
   cp .env.example .env
   nano .env
   ```

3. Generate files for deployment:
   
   Based on those variables, we will use a script to create all the required config files:
   ```bash
   pip install dotenv
   python generate_config.py
   ```

4. **Required** You need an hosting server for the ISO file that will be downloaded later.
   
   Suggestion: Use this docker run cmd on a server with Docker installed
   ```bash
   mkdir files
   touch ./files/index.html
   sudo docker run -it --rm -d -p 8033:80 --name image-serv -v ./files:/usr/share/nginx/html nginx
   ```

5. Create a RedHat account on console.redhat.com

6. Get pull-secret on RedHat Website

   https://console.redhat.com/openshift/install/pull-secret download as "pull-secret.txt" and put it inside the folder

7. Get token on RedHat Website 

   https://console.redhat.com/openshift/token, click 'Load Token' and download as "token.txt" and put it inside the folder

8. Create an SSH key and make sure it's called ssh.pub and inside the folder
   ```bash 
   ssh-keygen -f ./ssh
   ```

9. Your directory should look like this:
   ```bash
   ❯ ls
   cluster.json          proxy.json            redfish.json          server.template.json  ssh.pub               web.json
   cluster.template.json proxy.template.json   redfish.template.json single.yaml           token.txt             web.template.json
   generate_config.py    pull-secret.txt       server.json           ssh                   tutorials             iserver
   configs    
   ```

10. Get iserver requirements:
   ```bash
   # pyenv shell 3.9.15 # tested on this specific python release
   pip install urllib3==1.25.8 # we have to force this version at the moment
   pip install webexteamssdk # this is missing for the requierements for iserver at the moment but needed
   pip install -r ./iserver/requirements.txt
   pip install python-novaclient
   ```

11. Configure iserver:
   ```bash
   cd iserver
   python iserver.py set ocp console --token ../token.txt --secret ../pull-secret.txt
   ```

12. Create the OpenShift Cluster:
   ```bash
   python iserver.py create ocp cluster bm --dir ../ --mode install
   ```

13. You can check the progress and the generated configuration: https://console.redhat.com/openshift/cluster-list

14. Go get a coffee as it will take some time ☕️ 