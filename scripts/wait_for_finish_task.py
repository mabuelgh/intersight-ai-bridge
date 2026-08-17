import json
import csv
import os
from dotenv import load_dotenv

import intersight
import urllib3
from intersight import signing
from intersight.configuration import JSON_SCHEMA_VALIDATION_KEYWORDS
from intersight.model.mo_mo_ref import MoMoRef
from intersight.api import workflow_api
from intersight.api import server_api
from intersight.api import compute_api
import argparse
import time
import sys


# Load environment variables
load_dotenv()

class IntersightConfig:
    def __init__(self):
        self.read_dot_env('.env')
        self.host = os.getenv('INTERSIGHT_HOST')
        self.api_key_id = os.getenv('INTERSIGHT_API_KEY_ID')
        self.private_key_path = os.getenv('INTERSIGHT_PRIVATE_KEY_PATH')
        self.organization = os.getenv('ORGANIZATION_NAME', 'default')
        self.server_name = os.getenv('SERVER_NAME')
        self.server_profile_name = os.getenv('SERVER_PROFILE_NAME')
        self.os_image = os.getenv('OS_IMAGE_NAME')
        self.scu_image = os.getenv('SCU_IMAGE_NAME')
        
        # Validate required environment variables
        if not self.api_key_id:
            raise ValueError("INTERSIGHT_API_KEY_ID environment variable is required")
        if not self.server_name:
            raise ValueError("SERVER_NAME environment variable is required")
        
    def read_dot_env(self, file_path):
        """Read environment variables from a .env file."""
        if os.path.exists(file_path):
            load_dotenv(dotenv_path=file_path)
        else:
            raise FileNotFoundError(f"{file_path} does not exist")

config = IntersightConfig()

urllib3.disable_warnings()
conf = intersight.Configuration(
    host=config.host,
    signing_info=intersight.signing.HttpSigningConfiguration(
        key_id=config.api_key_id,
        private_key_path=config.private_key_path,
        signing_scheme=signing.SCHEME_HS2019,
        signing_algorithm=signing.ALGORITHM_ECDSA_MODE_FIPS_186_3,
        signed_headers=[
            signing.HEADER_REQUEST_TARGET,
            signing.HEADER_DATE,
            signing.HEADER_HOST,
            signing.HEADER_DIGEST
        ]
    )
)

conf.disabled_client_side_validations = ",".join(JSON_SCHEMA_VALIDATION_KEYWORDS)
conf.verify_ssl = False
conf.access_token = None
conf.proxy = os.getenv('PROXY_URL')
apiClient = intersight.ApiClient(conf)

MAX_OBJECTS_PER_FETCH_CALL = 100

def fetch_sp(sp_name):
    api = server_api.ServerApi(apiClient)
    call = "get_server_profile_list"
    filter = f"Name eq '{sp_name}'"
    try:
        obj_result = getattr(api, call)(filter=filter, orderby='CreateTime').results
        # Using the latest by default
        return obj_result[-1]
    except Exception as e:
        print(e)

def fetch_server_moid(server_name):
    """Resolve the Moid of a physical server (rack unit or blade) by name."""
    api = compute_api.ComputeApi(apiClient)
    call = "get_compute_physical_summary_list"
    filter = f"Name eq '{server_name}'"
    try:
        obj_result = getattr(api, call)(filter=filter).results
        if obj_result:
            return obj_result[-1].moid
    except Exception as e:
        print(e)
    return None


def fetch_os_install_workflow(server_moid):
    """Fetch the latest 'Operating System Install' workflow.WorkflowInfo for a server.

    Querying workflow.WorkflowInfo directly (instead of view.Server) avoids
    deserialization/discriminator errors that can occur when the view API
    response schema does not match what this SDK version expects.
    """
    api = workflow_api.WorkflowApi(apiClient)
    filter = (
        "Name eq 'Operating System Install' and "
        f"AssociatedObject.Moid eq '{server_moid}'"
    )
    try:
        obj_result = api.get_workflow_workflow_info_list(
            filter=filter, orderby='CreateTime desc', top=1
        ).results
        if obj_result:
            return obj_result[0]
        return None
    except Exception as e:
        print(e)
        return None


def main():
    parser = argparse.ArgumentParser(description='Wait for the finish of a task in Intersight')
    parser.add_argument('--deploysp', action='store_true', help='Deploy Server Profile')
    parser.add_argument('--deployos', action='store_true', help='Deploy OS Image')
    args = parser.parse_args()
    # print("Wait 0 0 0 Start")
    iteration = 0
    # Check for Deploy Server Profile
    if args.deploysp:
        while True:
            mo = fetch_sp(config.server_profile_name)

            if mo.config_context.config_state in ["Associated"]:
                print("Deploy Server Profile task completed successfully.")
                sys.exit(0)
            elif mo.config_context.config_state in ["Failed", "Error"]:
                print("Deploy Server Profile task failed.")
                sys.exit(1)
            elif mo.config_context.config_state in ["Activating", "Configuring"]:
                iteration += 1
                time.sleep(10)  # Wait for 10 seconds before checking again
            else:
                iteration += 1
                time.sleep(10)  # Wait for 10 seconds before checking again
            if iteration > 100:
                print("Deploy Server Profile task is taking too long.")
                sys.exit(2)

    if args.deployos:
            server_moid = fetch_server_moid(config.server_name)
            if not server_moid:
                print(f"Server '{config.server_name}' not found.")
                sys.exit(2)

            iteration_task = 0
            while True:
                wk_info = fetch_os_install_workflow(server_moid)
                if wk_info is None:
                    iteration_task += 1
                elif wk_info.status in ["COMPLETED"]:
                    print("Deploy OS Image task completed successfully.")
                    sys.exit(0)
                elif wk_info.status in ["TERMINATED", "FAILED"]:
                    print("Deploy OS Image task failed.")
                    sys.exit(1)
                elif wk_info.status in ["RUNNING"]:
                    iteration += 1
                    print("Deploy OS Image task is running.")
                else:
                    iteration += 1

                if iteration > 100:
                    print("Deploy OS Image task is taking too long.")
                    sys.exit(2)
                if iteration_task > 3:
                    print("Deploy OS Image task not found.")
                    sys.exit(2)
                time.sleep(60)  # Wait for 60 seconds before checking again
    

if __name__ == "__main__":
    main()