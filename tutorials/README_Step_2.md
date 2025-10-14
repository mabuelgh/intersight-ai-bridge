# Intersight AI Bridge - Step 2 Detailed Instructions

## Step 2: Install the Operating System through Intersight OS Install feature
(Can be skipped if you prefer manual installation or are not using Intersight.)  

### 1. Modify the cfg file to your environement, recommended things to change:
- Hashed passsword and default username
- Network interface settings : remove or change VLAN, put DHCP mode or manual IP
- Change the Proxy address or remove it
- Adjust the timezone

### 2. Download the recommended ISO
- [Ubuntu](https://old-releases.ubuntu.com/releases/22.04/)
- [Cisco CSU](https://software.cisco.com/download/home/286331885/type/283137444/release/6.3(2c))

Recommended ISOs:  
- `ubuntu-22.04.2-live-server-amd64.iso`  
- `ucs-scu-6.3.2c.iso`

### 3. Use the Software Repository of Intersight
- Open Intersight
- Go to System > Software Repository
- Add the OS Image Link of the downloaded Ubuntu (you can put the image on any NFS, CIFS or HTTP like EasyUCS or IMM Transition Tool)
- Add the SCU Link of the downloaded SCU (you can put the image on any NFS, CIFS or HTTP like EasyUCS or IMM Transition Tool)
- Upload the OS Configuration file (the cfg file modified in step 1)

### 4. Install Operating System
- Go to the target server, go to Action, select "Install Operating System"
- Select the OS, select "Custom" configuration
- Select the cfg file
- Select the SCU
- Select the installation target "M.2 MStorBootVd"
- Click on Install

**Note**: This process will take some time.
