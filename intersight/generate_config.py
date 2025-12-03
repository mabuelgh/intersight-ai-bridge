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

def generate_ubuntu_config(template_path="ubuntu-ai-config.template", output_path="ubuntu-ai-config.cfg"):
    """Generate Ubuntu autoinstall config from template"""
    load_dotenv()
    
    env_vars = {
        'PROXY_URL': os.getenv('PROXY_URL'),
        'SERVER_INTERFACE': os.getenv('SERVER_INTERFACE'),
        'SERVER_IP_ADDRESS': os.getenv('SERVER_IP_ADDRESS'),
        'SERVER_GATEWAY': os.getenv('SERVER_GATEWAY'),
        'PRIMARY_DNS': os.getenv('PRIMARY_DNS'),
        'SERVER_HOSTNAME': os.getenv('SERVER_HOSTNAME', 'ai-server'),
        'SERVER_TIMEZONE': os.getenv('SERVER_TIMEZONE', 'Europe/Paris')
    }
    
    generate_from_template(template_path, output_path, env_vars)

def generate_json_config(template_path="config.template.json", output_path="config.json"):
    """Generate JSON config from template"""
    load_dotenv()
    
    env_vars = {
        'SERVER_PROFILE_NAME': os.getenv('SERVER_PROFILE_NAME'),
        'SERVER_SERIAL': os.getenv('SERVER_SERIAL'),
        'NATIVE_VLAN_ID': os.getenv('NATIVE_VLAN_ID'),
        'ALLOWED_VLANS': os.getenv('ALLOWED_VLANS'),
        'INBAND_VLAN_ID': os.getenv('INBAND_VLAN_ID'),
        'MGMT_IP_FROM': os.getenv('MGMT_IP_FROM'),
        'MGMT_IP_TO': os.getenv('MGMT_IP_TO'),
        'MGMT_GATEWAY': os.getenv('MGMT_GATEWAY'),
        'MGMT_PRIMARY_DNS': os.getenv('MGMT_PRIMARY_DNS'),
        'MGMT_SECONDARY_DNS': os.getenv('MGMT_SECONDARY_DNS')
    }
    
    generate_from_template(template_path, output_path, env_vars)

def main():
    parser = argparse.ArgumentParser(description='Generate configuration files from templates')
    parser.add_argument('--ubuntu', action='store_true', help='Generate Ubuntu config')
    parser.add_argument('--json', action='store_true', help='Generate JSON config')
    parser.add_argument('--all', action='store_true', help='Generate all configs')
    
    args = parser.parse_args()
    
    if args.all or args.ubuntu:
        generate_ubuntu_config()
    
    if args.all or args.json:
        generate_json_config()
    
    if not any([args.ubuntu, args.json, args.all]):
        print("Please specify --ubuntu, --json, or --all")
        parser.print_help()

if __name__ == "__main__":
    main()