# api/createDataset.py
import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def create_dataset_service(name, workspace_id, desc, creds, version, host):
    method = "POST"
    action = "CreateDataset"
    service = "app"
    url_path = '/'

    # 1. เตรียม Body Data ตามเอกสาร
    data = {
        "Name": name,
        "WorkspaceID": workspace_id,
        "Description":  desc,
        "DirectoryID": "default", 
        "Icon": "upload/full/36/b9/11329df8034b1741c2a2f5ab9bac545ee6b4e2a26da8f8b43ce32f895225",
        "IndexingTechnique": 0,
        "Models": {
            "EmbedID": "d394otlutcss738d8qfg",
            "LlmID": "d393no652vvc73d72a20"
        },
        "SpaceType": 1
    }
    
    print("CreateDataset Body Data:", data)
    json_body = json.dumps(data)
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()
    print("CreateDataset Body Hash:", body_hash)
    # 2. ลงลายเซ็น V4
    sign = SignerV4()
    param = SignParam()
    param.path = url_path
    param.method = method
    param.host = host
    param.body = body_hash
    param.query = OrderedDict([('Action', action), ('Version', version)])
    param.header_list = OrderedDict([('Host', host)])

    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)
    url = f"https://{host}{url_path}?{resulturl}"
    print("CreateDataset URL:", url)

    try:
        resp = requests.request(method, url=url, headers={'Content-Type': 'application/json'}, data=json_body, verify=True, timeout=30)
        
        print("CreateDataset Response Status Code:", resp.status_code)
    
        if resp.status_code != 200:
            print(resp.text)
            return None
        
        response_json = resp.json()
        if response_json.get("ResponseMetadata", {}).get("Error") is None:
            return response_json.get("Result", {}).get("Id")
        else:
            print(f"CreateDataset API Error: {response_json}")
            return None
            
    except Exception as e:
        print(f"CreateDataset Request failed: {e}")
        return None