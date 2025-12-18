import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def verify_dataset_exists_service(name, workspace_id, creds, version, host):
    method = "POST"
    action = "ValidateDatasetExist"
    service = "app"
    url_path = '/'

    # 1. เตรียม Body Data (ชื่อต้องตรงกับที่ต้องการเช็ค)
    data = {
        "Name": name,
        "WorkspaceID": workspace_id,
    }

    # ทำ Compact JSON เพื่อป้องกันปัญหา Signature
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
        resp = requests.request(method, url=url, headers={'Content-Type': 'application/json'}, data=json_body, verify=True)
        
        if resp.status_code != 200:
            print(f"VerifyDataset API Error: {resp.text}")
            return False

        response_json = resp.json()
        return response_json.get("Result", {}).get("Exist", False)
    except Exception as e:
        print(f"VerifyDataset Request failed: {e}")
        return False