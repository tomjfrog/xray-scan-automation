import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global variables
BASE_URL = "https://tomjfrog.jfrog.io/xray/api"
ARTIFACTORY_NAME = "default"

# Headers for the requests
headers = {
    "Content-Type": "application/json"
}


# Function to read the access token from a file
def load_access_token(file_path):
    try:
        with open(file_path, 'r') as file:
            token = file.read().strip()
        return token
    except FileNotFoundError:
        logger.error(f"Access token file '{file_path}' not found.")
        raise
    except Exception as e:
        logger.error(f"An error occurred while reading the access token file: {e}")
        raise


# Mapping function
def get_prefix_for_pkg_type(pkg_type):
    # Sample mapping
    mapping = {
        "Docker": "docker://",
        "Maven": "gav://"
        # Add more mappings here as needed
    }
    return mapping.get(pkg_type, "default://")


def get_artifact_component_id(path, token):
    # Prefix the path with "default://"
    prefixed_path = f"default://{path}"

    # Endpoint for the POST request
    post_url = f"{BASE_URL}/v1/dependencyGraph/artifact"
    logger.info(f"Making POST request to URL: {post_url} with body: {{'path': '{prefixed_path}'}}")

    # JSON body for the POST request
    json_body = {
        "path": prefixed_path
    }

    # Make the POST request
    response = requests.post(post_url, headers={**headers, "Authorization": f"Bearer {token}"}, json=json_body)

    # Log the response details
    logger.info(f"Response Status Code: {response.status_code}")
    logger.info(f"Response Body: {response.text}")

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract the component_id and pkg_type from the response JSON
        component_id = data['artifact']['component_id']
        pkg_type = data['artifact']['pkg_type']
        return component_id, pkg_type
    else:
        raise Exception(
            f"POST request to /v1/dependencyGraph/artifact failed with status code {response.status_code} and message {response.text}")


def scan_artifact(component_id, pkg_type, token):
    # Get the prefix based on the pkg_type
    prefix = get_prefix_for_pkg_type(pkg_type)

    # Prefix the component ID with the determined prefix
    prefixed_component_id = f"{prefix}{component_id}"

    # Endpoint for the POST request
    post_url = f"{BASE_URL}/v1/scanArtifact"
    logger.info(f"Making POST request to URL: {post_url} with body: {{'componentID': '{prefixed_component_id}'}}")

    # JSON body for the POST request
    json_body = {
        "componentID": prefixed_component_id
    }

    # Make the POST request
    response = requests.post(post_url, headers={**headers, "Authorization": f"Bearer {token}"}, json=json_body)

    # Log the response details
    logger.info(f"Response Status Code: {response.status_code}")
    logger.info(f"Response Body: {response.text}")

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"POST request to /v1/scanArtifact failed with status code {response.status_code} and message {response.text}")


def process_paths_from_file(input_file, token_file):
    # Load the access token
    token = load_access_token(token_file)

    try:
        with open(input_file, 'r') as file:
            paths = file.readlines()

        for path in paths:
            path = path.strip()  # Remove any leading/trailing whitespace
            if path:  # Only process non-empty lines
                logger.info(f"Processing path: {path}")
                try:
                    # Get the component ID and pkg_type from the first API call
                    component_id, pkg_type = get_artifact_component_id(path, token)
                    logger.info(f"Component ID: {component_id}, Package Type: {pkg_type}")

                    # Use the component ID and pkg_type in the second API call
                    scan_result = scan_artifact(component_id, pkg_type, token)
                    logger.info(f"Scan result: {scan_result}")

                except Exception as e:
                    logger.error(f"An error occurred while processing path {path}: {e}")

    except FileNotFoundError:
        logger.error(f"Input file '{input_file}' not found.")


def main():
    input_file = "input.txt"  # Specify your input file name here
    token_file = "access_token.txt"  # Specify your token file name here
    process_paths_from_file(input_file, token_file)


if __name__ == "__main__":
    main()