#!/usr/bin/env python

import json
import csv
import os
from dotenv import load_dotenv

import intersight
import urllib3
from intersight import signing
from intersight.configuration import JSON_SCHEMA_VALIDATION_KEYWORDS
from intersight.model.mo_mo_ref import MoMoRef
from intersight.api import firmware_api
from intersight.api import organization_api
from intersight.api import compute_api
from intersight.api import softwarerepository_api
from intersight.api import bulk_api
from intersight.model.os_install import OsInstall
from intersight.model.os_answers import OsAnswers
from intersight.model.os_virtual_drive import OsVirtualDrive
from intersight.model.bulk_request import BulkRequest
from intersight.model.bulk_rest_sub_request import BulkRestSubRequest


# Load environment variables
load_dotenv()

class IntersightConfig:
    def __init__(self):
        self.host = os.getenv('INTERSIGHT_HOST')
        self.api_key_id = os.getenv('INTERSIGHT_API_KEY_ID')
        self.private_key_path = os.getenv('INTERSIGHT_PRIVATE_KEY_PATH')
        self.organization = os.getenv('ORGANIZATION_NAME', 'default')
        self.server_name = os.getenv('SERVER_NAME')
        self.os_image = os.getenv('OS_IMAGE_NAME')
        self.scu_image = os.getenv('SCU_IMAGE_NAME')
        
        # Validate required environment variables
        if not self.api_key_id:
            raise ValueError("INTERSIGHT_API_KEY_ID environment variable is required")
        if not self.server_name:
            raise ValueError("SERVER_NAME environment variable is required")

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
apiClient = intersight.ApiClient(conf)

MAX_OBJECTS_PER_FETCH_CALL = 100



def fetch_scu_moid(name):
    # firmware.ServerConfigurationUtilityDistributable
    api = firmware_api.FirmwareApi(apiClient)
    call = "get_firmware_server_configuration_utility_distributable_list"
    filter = f"Name eq '{name}'"
    try:
        obj_result = getattr(api, call)(filter=filter).results
        return obj_result[0].moid
    except Exception as e:
        print(e)

def fetch_org_moid(name):
    api = organization_api.OrganizationApi(apiClient)
    call = "get_organization_organization_list"
    filter = f"Name eq '{name}'"
    try:
        obj_result = getattr(api, call)(filter=filter).results
        return obj_result[0].moid
    except Exception as e:
        print(e)

def fetch_server_moid(name):
    api = compute_api.ComputeApi(apiClient)
    call = "get_compute_physical_summary_list"
    filter = f"Name eq '{name}'"
    try:
        obj_result = getattr(api, call)(filter=filter).results
        return obj_result[0].moid, obj_result[0].source_object_type
    except Exception as e:
        print(e)

def fetch_os_moid(name):
    api = softwarerepository_api.SoftwarerepositoryApi(apiClient)
    call = "get_softwarerepository_operating_system_file_list"
    filter = f"Name eq '{name}'"
    try:
        obj_result = getattr(api, call)(filter=filter).results
        return obj_result[0].moid
    except Exception as e:
        print(e)

def import_config_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        config_data = f.read()
    config_data = config_data
    return config_data

def add_os_install(server_moid, server_type, org_moid, OS_moid, SCU_moid, config_data):
    # Deploy OS Install
    api = bulk_api.BulkApi(apiClient)

    os_install = OsInstall()
    os_install.install_method = "vMedia"
    os_install.image = MoMoRef(moid=OS_moid, object_type="softwarerepository.OperatingSystemFile")
    os_install.osdu_image = MoMoRef(moid=SCU_moid, object_type="firmware.ServerConfigurationUtilityDistributable")
    os_install.override_secure_boot = True
    os_install.organization = MoMoRef(moid=org_moid, object_type="organization.Organization")
    os_install.answers = OsAnswers(
        source="File",
        answer_file=config_data
    )
    os_install.install_target = OsVirtualDrive(class_id="os.VirtualDrive", object_type="os.VirtualDrive", name="MStorBootVd",storage_controller_slot_id="MSTOR-RAID", id="0")
    os_install.server = MoMoRef(moid=server_moid, object_type=server_type)


    sub_request = BulkRestSubRequest(object_type="bulk.RestSubRequest", body=os_install)
    bulk_request = BulkRequest(verb="POST", uri="/v1/os/Installs",requests=[sub_request])

    try:
        api_response = api.create_bulk_request(bulk_request)
        print("OS Install deployment initiated successfully.")
    except Exception as e:
        print(e)


def main():
    print(f"Using Intersight host: {config.host}")
    print(f"Organization: {config.organization}")
    print(f"Server: {config.server_name}")
    print(f"OS Image: {config.os_image}")
    print(f"SCU Image: {config.scu_image}")
    
    SCU_moid = fetch_scu_moid(config.scu_image)
    org_moid = fetch_org_moid(config.organization)
    OS_moid = fetch_os_moid(config.os_image)
    server_moid, server_type = fetch_server_moid(config.server_name)
    config_data = import_config_file('./ubuntu-ai-config.cfg')
    add_os_install(server_moid, server_type, org_moid, OS_moid, SCU_moid, config_data)

if __name__ == "__main__":
    main()
