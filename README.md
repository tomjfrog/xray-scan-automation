# Xray Scan Automation
## Setup
1. In the root of the project, add a valid Token with permissions required to Scan an Artifact via Xray's `scanArtifact` REST API.
2. Remove the `.example` suffix to the file.  The file name should be `access_token.txt`
3. Add in the paths of a list of Artifacts that need to be scanned in `input.txt`.  Refer to this screenshot as an example of where to find this value in the UI:
![image info](./Path-Value-Source.png)

## Run
Run this script locally by executing `<name-of-python-executable> ./main.py`