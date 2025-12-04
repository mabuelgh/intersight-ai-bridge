# Intersight AI Bridge - Step 1 Detailed Instructions

## Step 1: Deploy the Server Profile on Intersight
(Can be skipped if you prefer manual installation or are not using Intersight.)
(This process is using [EasyUCS](https://github.com/vesposito/easyucs))

### 1. Install EasyUCS to automate Server Profile deployment:
- On a system that has access to the Intersight account:
```bash
git clone https://github.com/mabuelgh/intersight-ai-bridge
cd cd intersight-ai-bridge/intersight
git clone https://github.com/vesposito/easyucs.git
```

- Install the python dependencies:
```bash
pip install -r easyucs/requirements.txt
pip install -r requirements.txt
```

### 2. Get an API Key on Intersight
- Open Intersight
- Go to Settings > Keys
- Click on **"Generate an API Key"**, put a description related to this project, select "schema version 3" and choose an expiration date
- Copy the API Key ID on a notepad 
- Download the Secret Key with the button "Save Secret Key to text file"
- Put the **SecretKey.txt** file inside the "intersight" folder

**Note**: The key has the same access to Intersight as the user who created it. Please use a user with write-access for this projet.

### 3. Deploy the JSON config file to Intersight

- Create a copy of ".env.example" and **modify that copy to match your environment**:
```bash
cp .env.example .env
nano .env
```
- Launch the config generation script:
```bash
python generate_config.py --json
```
- Execute EasyUCS script inside */easyucs* folder : 
```bash
python easyucs/easyucs.py config push -i eu-central-1.intersight.com -a "API Key ID" -k ./SecretKey.txt -t intersight -f ./config.json
```
**Note**: For SaaS Intersight in the US, use *intersight.com*.<br>
For SaaS Intersight in the EU, use *eu-central-1.intersight.com*.

### 4. Deploy Server Profile
- Execute the following script to deploy the Server Profile and apply the changes on reboot:
```bash
python deploy_server_profile.py
```
