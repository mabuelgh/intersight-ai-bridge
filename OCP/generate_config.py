#!/usr/bin/env python
"""
Simple template generator for Intersight configuration files
This script replaces ${VARIABLE} placeholders in templates with environment variables.
"""

import os
import argparse
from dotenv import load_dotenv
from string import Template

def generate_from_template(template_path, output_path, env_vars):
    """Generate config file from template using environment variables"""
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    
    # Substitute environment variables
    try:
        config_content = template.substitute(env_vars)
    except KeyError as e:
        print(f"Warning: Missing environment variable {e}, using template as-is")
        config_content = template.safe_substitute(env_vars)
    
    with open(output_path, 'w') as f:
        f.write(config_content)
    
    print(f"Generated {output_path} from {template_path}")

def generate_json_config(template_path="config.template.json", output_path="config.json"):
    """Generate JSON config from template"""
    load_dotenv()
    
    if output_path == "cluster.json":
        env_vars = {
            'CLUSTER_NAME': os.getenv('CLUSTER_NAME'),
            'OPENSHIFT_VERSION': os.getenv('OPENSHIFT_VERSION'),
            'CPU_ARCH': os.getenv('CPU_ARCH'),
            'BASE_DOMAIN': os.getenv('BASE_DOMAIN'),
            'CLUSTER_NETWORK_CIDR': os.getenv('CLUSTER_NETWORK_CIDR'),
            'CLUSTER_NETWORK_HOST_PREFIX': os.getenv('CLUSTER_NETWORK_HOST_PREFIX'),
            'SERVICE_NETWORK_CIDR': os.getenv('SERVICE_NETWORK_CIDR'),
            'MACHINE_NETWORK_GATEWAY': os.getenv('MACHINE_NETWORK_GATEWAY'),
            'ISO': os.getenv('ISO'),
            'NTP': os.getenv('NTP'),
            'DNS_IP': os.getenv('DNS_IP'),
            'DNS_SEARCH': os.getenv('DNS_SEARCH')
        }
    if output_path == "proxy.json":
        env_vars = {
            'HTTP_PROXY': os.getenv('HTTP_PROXY'),
            'HTTPS_PROXY': os.getenv('HTTPS_PROXY'),
            'NO_PROXY': os.getenv('NO_PROXY')
        }
    if output_path == "proxy.json":
        env_vars = {
            'HTTP_PROXY': os.getenv('HTTP_PROXY'),
            'HTTPS_PROXY': os.getenv('HTTPS_PROXY'),
            'NO_PROXY': os.getenv('NO_PROXY')
        }
    if output_path == "redfish.json":
        env_vars = {
            'IMC_USERNAME': os.getenv('IMC_USERNAME'),
            'IMC_PASSWORD': os.getenv('IMC_PASSWORD')
        }
    if output_path == "server.json":
        env_vars = {
            'ENDPOINT_TYPE': os.getenv('ENDPOINT_TYPE'),
            'INVENTORY_ID': os.getenv('INVENTORY_ID'),
            'ENDPOINT_IP': os.getenv('ENDPOINT_IP'),
            'DESIRED_OS_IP_ADDRESS': os.getenv('DESIRED_OS_IP_ADDRESS'),
            'VLAN': os.getenv('VLAN'),
            'SERVER_INTERFACE_NAME': os.getenv('SERVER_INTERFACE_NAME'),
            'SERVER_INTERFACE_MAC': os.getenv('SERVER_INTERFACE_MAC'),
            'NMSTATE': os.getenv('NMSTATE'),
            'CLUSTER_NAME': os.getenv('CLUSTER_NAME')
        }
    if output_path == "web.json":
        env_vars = {
            'WEB_USERNAME': os.getenv('WEB_USERNAME'),
            'WEB_PASSWORD': os.getenv('WEB_PASSWORD'),
            'WEB_IP': os.getenv('WEB_IP'),
            'IMAGE_BASE_URL': os.getenv('IMAGE_BASE_URL'),
            'IMAGE_UPLOAD_DIRECTORY': os.getenv('IMAGE_UPLOAD_DIRECTORY')
        }
        
    generate_from_template(template_path, output_path, env_vars)

def main():
    parser = argparse.ArgumentParser(description='Generate configuration files from templates')
    # parser.add_argument('--json', action='store_true', help='Generate JSON config')
    # parser.add_argument('--all', action='store_true', help='Generate all configs')
    # args = parser.parse_args()

    generate_json_config(template_path="cluster.template.json", output_path="cluster.json")
    generate_json_config(template_path="proxy.template.json", output_path="proxy.json")
    generate_json_config(template_path="redfish.template.json", output_path="redfish.json")
    generate_json_config(template_path="server.template.json", output_path="server.json")
    generate_json_config(template_path="web.template.json", output_path="web.json")
    
"""     if args.all or args.json:
        generate_json_config()
    
    if not any([args.ubuntu, args.json, args.all]):
        print("Please specify --ubuntu, --json, or --all")
        parser.print_help() """

if __name__ == "__main__":
    main()