import os
import yaml
import json
import uuid
from dotenv import load_dotenv

load_dotenv()

import vcr

import pytest
import fairly

# Requires develop to have .env file with FAIRLY_FIGSHARE_TOKEN
FIGSHARE_TOKEN = os.environ.get("FAIRLY_FIGSHARE_TOKEN")
ZENODO_TOKEN = os.environ.get("FAIRLY_ZENODO_TOKEN")

# load clients from supported clients
TEMPLATES = os.listdir("./src/fairly/data/templates")

# We generate a unique string that we can use to populate metadata for testing
ustring = str(uuid.uuid4())

def setup_fairly_config_for_testing():
    """Create a fairly config file for testing
    for this we need to create also the directory where the config file is stored
    We also create a backup of the config file before running the tests to recover prior existing config
    """
    # create ~/.fairly folder if it does not exist
    if not os.path.exists(os.path.expanduser("~/.fairly")):
        os.makedirs(os.path.expanduser("~/.fairly"))
    
    else: print("fairly config folder already exists")
   
    # copy existing ~/.fairly/config.json to ~/.fairly/config.json.backup
    # We do this to test the config file creation and loading
    try: 
        # Create the config file if it does not exist
        if not os.path.exists(os.path.expanduser("~/.fairly/config.json")):
            print("fairly config file does not exist")
            with open(os.path.expanduser("~/.fairly/config.json"), "w") as f:
                # create dummy config file using environment variables
                config = {}
                config['4tu'] = { 'token' : FIGSHARE_TOKEN }
                config['zenodo'] = { 'token' : ZENODO_TOKEN }
                f.write(json.dumps(config))

        with open(os.path.expanduser("~/.fairly/config.json.backup"), "w") as f:
            json.dump(config, f)

    except FileNotFoundError:
        print("No config file found, skipping backup")

def create_manifest_from_template(template_file: str) -> None:
    """Create a manifest file from a template file
    Parameters
    ----------
    template_file : str
        Name of the template file in yaml format e.g. figshare.yaml
        the file is extracted from the templates folder
    """
    with open(f"./src/fairly/data/templates/{template_file}", "r") as f:
        template = f.read()
        template = yaml.safe_load(template)
        template['metadata']['title'] = "My fairly test"
        template['metadata']['description'] = ustring
        # Add files key to the manifest so that files are added to the dataset object
        template['files'] = { 'excludes': [], 'includes': ["*.txt"] }
        if template_file == "figshare.yaml":
            template['metadata']['authors'] = [ ustring ]
        if template_file == "zenodo.yaml":
            template['metadata']['creators'] = [ { "name": ustring } ]
            template['metadata']['authors'] = [ {"name" : ustring } ]
            template['metadata']['description'] = ustring
            template['metadata']['license'] = 'cc-by-nc-4.0'
            template['metadata']['type'] = 'dataset'
            # template dates
            template['metadata']['publication_date'] = '2020-01-01'

    with open(f"./tests/fixtures/dummy_dataset/manifest.yaml", "w") as f:
        f.write(yaml.dump(template))

# Set testing flag
fairly.TESTING = True

if __name__ == "__main__":
    setup_fairly_config_for_testing()

