# Intersight AI Bridge - Step 2 Detailed Instructions

## Step 2: Install the Operating System through Intersight OS Install feature
(Can be skipped if you prefer manual installation or are not using Intersight.)  

### 1. Download the recommended ISO
- [Ubuntu](https://old-releases.ubuntu.com/releases/22.04/)
- [Cisco CSU](https://software.cisco.com/download/home/286331885/type/283137444/release/6.3(2c))

Recommended ISOs:  
- `ubuntu-24.04.3-live-server-amd64.iso`
- `ucs-scu-7.1.4.250100.iso`

### 2. Modify the env file to your environement:

- Install the python dependencies:
```bash
cd intersight
pip install -r requirements.txt
```
- If not already done, create a copy of ".env.example" and **modify that copy to match your environment**:
```bash
cp .env.example .env
nano .env
```
- Launch the config generation script:
```bash
python generate_config.py --ubuntu
```

### 3. Use the Software Repository of Intersight
- Open Intersight
- Go to System > Software Repository
- Add the OS Image Link of the downloaded Ubuntu (you can put the image on any NFS, CIFS or HTTP like EasyUCS or IMM Transition Tool)
- Add the SCU Link of the downloaded SCU (you can put the image on any NFS, CIFS or HTTP like EasyUCS or IMM Transition Tool)
- Only if you do step 4bis afterward: Upload the OS Configuration file (the cfg file modified in step 1)

### 4. Install Operating System with Python
- Make sure Intersight package is installed 
```python
pip install intersight
```
- Execute the python script os_install.py, make sure to match the global variables to your environnement
```python
python os_install.py
```

### 4bis. Install Operating System manually
- Go to the target server, go to Action, select "Install Operating System"
- Select the OS, select "Custom" configuration
- Select the cfg file
- Select the SCU
- Select the installation target "M.2 MStorBootVd"
- Click on Install

**Note**: This process will take some time.
