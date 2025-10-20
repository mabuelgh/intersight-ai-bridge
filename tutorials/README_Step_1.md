# Intersight AI Bridge - Step 1 Detailed Instructions

## Step 1: Deploy the Server Profile on Intersight
(Can be skipped if you prefer manual installation or are not using Intersight.)
(This process is using [EasyUCS](https://github.com/vesposito/easyucs))

### 1. Install EasyUCS to automate Server Profile deployment:
On a computer that has access to the Intersight account:

```bash
git clone https://github.com/vesposito/easyucs.git
```

Install the python dependencies:
```bash
cd easyucs
pip install -r requirements.txt
```

### 2. Get an API Key on Intersight
- Open Intersight
- Go to Settings > Keys
- Click on **"Generate an API Key"**, put a description related to this project, select "schema version 3" and choose an expiration date
- Copy the API Key ID on a notepad 
- Download the Secret Key with the button "Save Secret Key to text file"

**Note**: The key has the same access to Intersight as the user who created it. Please use a user with write-access for this projet.

### 3. Deploy the JSON config file to Intersight

- Download the *[config.json](/intersight-files/config.json)* file and put it inside */easyucs* folder
- **Modify the json file** to match your environment:
  - VLAN: **541 by default**, look for "allowed_vlans" key
  - Serial Number assigned to the Server Profile: **WZP2708AIA by default**, look for "server_pre_assign_by_serial" key
  - Management IP: **10.48.54.80 by default**, look for "ipv4_blocks" key

- Put the **SecretKey.txt** file inside the same folder
- Execute EasyUCS script inside */easyucs* folder : 
```python
python easyucs.py config push -i eu-central-1.intersight.com -a "API Key ID" -k ./SecretKey.txt -t intersight -f ./config.json
```
**Note**: For SaaS Intersight in the US, use *intersight.com*.<br>
For SaaS Intersight in the EU, use *eu-central-1.intersight.com*.

### 4. Deploy Server Profile
*Detailed automated instructions will be added here soon.*

Select the Server Profile's actions, then select **deploy with reboot**.

