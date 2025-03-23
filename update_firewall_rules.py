import requests
import base64
import yaml
import os
import logging
import oci
from oci.config import from_file

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger
logger = logging.getLogger(__name__)

# Log the start of the script
logger.info("Starting the firewall update script...")

def get_env_var(var_name: str) -> str:
    """Get the value of the environment variable."""
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set.")
    return value


def get_file_contents(GITHUB_TOKEN: str, GITHUB_API_URL: str) -> dict:
    """Fetch the file's current contents and metadata."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)
    response.raise_for_status()
    return response.json()

def get_public_ip() -> str:
    try:
        response = requests.get("https://api.ipify.org?format=text")
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
        return None

def update_ip(data: dict, public_ip: str) -> dict:
    """Update the IP address in the YAML file."""
    data['spec']['ingress'][0]['fromCIDRSet'][0]['cidr'] = f"{public_ip}/32"  
    return data

def update_file(updated_content: str, sha: str, GITHUB_TOKEN: str, GITHUB_API_URL: str, BRANCH_NAME: str) -> dict:
    """Push the updated file back to GitHub."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {
        "message": "Update Gateway Policy via script",
        "content": base64.b64encode(updated_content.encode("utf-8")).decode("utf-8"),
        "sha": sha,
        "branch": BRANCH_NAME
    }
    response = requests.put(GITHUB_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def update_oci_nsg(NSG_ID: str, NSG_RULE_ID: str, public_ip: str, OCI_CONFIG: str) -> None:

    # Set the configuration
    config = from_file(file_location=OCI_CONFIG)

    # Initialize service client with default config file
    core_client = oci.core.VirtualNetworkClient(config)

    # Update the network security group security rules
    update_network_security_group_security_rules_response = core_client.update_network_security_group_security_rules(
        network_security_group_id=NSG_ID,
        update_network_security_group_security_rules_details=oci.core.models.UpdateNetworkSecurityGroupSecurityRulesDetails(
            security_rules=[
                oci.core.models.UpdateSecurityRuleDetails(
                    direction = "INGRESS",
                    id = NSG_RULE_ID,
                    protocol = "all",
                    description = "Allow Traffic from home",
                    destination = None,
                    destination_type = None,
                    icmp_options = None,
                    is_stateless=False,
                    source=f"{public_ip}/32",
                    source_type="CIDR_BLOCK",
                    tcp_options= None,
                    udp_options= None
                    )]))


def main():
    # Set the environment variables
    GITHUB_TOKEN =get_env_var("GITHUB_TOKEN")
    REPO_OWNER = get_env_var("REPO_OWNER")
    REPO_NAME = get_env_var("REPO_NAME")
    FILE_PATH = get_env_var("FILE_PATH")  
    BRANCH_NAME = get_env_var("BRANCH_NAME")  
    NSG_ID = get_env_var('NSG_ID')
    NSG_RULE_ID = get_env_var('NSG_RULE_ID')
    OCI_CONFIG = get_env_var('OCI_CONFIG')
    MGMT_NSG_RULE_ID = get_env_var('MGMT_NSG_RULE_ID')
    MGMT_NSG_ID = get_env_var('MGMT_NSG_ID')
    MGMT_OCI_CONFIG = get_env_var('MGMT_OCI_CONFIG')

    # API Base URL
    GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

    # Step 1: Fetch the current YAML file content
    # Log the start of the script
    logger.info("Fetching the current Gateway API Network Policy...")
    file_data = get_file_contents(GITHUB_TOKEN, GITHUB_API_URL)
    sha = file_data["sha"]
    encoded_content = file_data["content"]
    decoded_content = base64.b64decode(encoded_content).decode("utf-8")
    
    # Step 2: Load and modify the YAML content
    yaml_data = yaml.safe_load(decoded_content)
    logger.info('Fetching the current public IP address...')
    public_ip = get_public_ip()
    logger.info(f'Public IP address: {public_ip}')
    logger.info('Updating the allowed IP addresses in the Gateway API Network Policy...')
    updated_ip_yaml = update_ip(yaml_data, public_ip)

    # Step 3: Serialize the updated YAML back to a string
    updated_content = yaml.dump(updated_ip_yaml, default_flow_style=False)

    
    # Step 4: Push the updated content back to GitHub
    logger.info('Pushing the updated Gateway API Network Policy to GitHub...')
    update_response = update_file(updated_content, sha,  GITHUB_TOKEN, GITHUB_API_URL, BRANCH_NAME)
    logger.info(f"Gateway API Network Policy updated successfully: {update_response['commit']['html_url']}")

    # Step 5: Update the OCI Network Security Group
    logger.info('Updating the Main OCI Network Security Group Rules...')
    update_oci_nsg(NSG_ID, NSG_RULE_ID, public_ip, OCI_CONFIG)
    logger.info('OCI Network Security Group updated successfully.')

    # Step 6: Update the OCI Network Security Group for mgmt cluster
    logger.info('Updating the MGMT OCI Network Security Group Rules...')
    update_oci_nsg(MGMT_NSG_ID, MGMT_NSG_RULE_ID, public_ip, MGMT_OCI_CONFIG)
    logger.info('OCI Network Security Group updated successfully.')

if __name__ == "__main__":
    main()
