# api/getDataset.py
import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def get_dataset_service(dataset_id, workspace_id, creds, version, host) -> dict:
    method = "POST"
    action = "GetDataset"
    service = "app"
    url_path = '/'

    # 1. เตรียม Body Data
    data = {
        "Id": dataset_id,
        "WorkspaceID": workspace_id
    }

    json_body = json.dumps(data)
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

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

    try:
        resp = requests.request(method, url=url, headers={'Content-Type': 'application/json'}, data=json_body, verify=True, timeout=30)
        resp.raise_for_status()
        response_json = resp.json()
        
        if response_json.get("ResponseMetadata", {}).get("Error") is None:
            return response_json.get("Result", {})
        else:
            print(f"GetDataset API Error: {response_json}")
            return None
    except Exception as e:
        print(f"GetDataset Request failed: {e}")
        return None