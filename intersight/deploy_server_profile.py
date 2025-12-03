#!/usr/bin/env python

import json
import csv
import os
from dotenv import load_dotenv

import intersight
import urllib3
from intersight import signing
from intersight.configuration import JSON_SCHEMA_VALIDATION_KEYWORDS
from intersight.api import server_api
from intersight.model.server_profile import ServerProfile


# Load environment variables
load_dotenv()

urllib3.disable_warnings()
conf = intersight.Configuration(
    host=os.getenv('INTERSIGHT_HOST'),
    signing_info=intersight.signing.HttpSigningConfiguration(
        key_id=os.getenv('INTERSIGHT_API_KEY_ID'),
        private_key_path=os.getenv('INTERSIGHT_PRIVATE_KEY_PATH'),
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



def deploy_sp(sp_moid):
    api = server_api.ServerApi(apiClient)
    server_profile = ServerProfile(moid=sp_moid)
    server_profile.scheduled_actions = [{"Action":"Deploy","ProceedOnReboot":True}]
    try:
        api_response = api.update_server_profile(moid=sp_moid, server_profile=server_profile)
        print(api_response)
    except Exception as e:
        print(e)


def fetch_sp_moid(name):
    api = server_api.ServerApi(apiClient)
    call = "get_server_profile_list"
    filter = f"Name eq '{name}'"
    try:
        obj_result = getattr(api, call)(filter=filter).results
        return obj_result[0].moid
    except Exception as e:
        print(e)


def main():
    server_profile_name = os.getenv('SERVER_PROFILE_NAME')
    sp_moid = fetch_sp_moid(server_profile_name)
    deploy_sp(sp_moid)


if __name__ == "__main__":
    main()
