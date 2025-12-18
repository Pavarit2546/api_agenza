import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def batch_get_dataset_service(dataset_ids, workspace_id, creds, version, host):
    method = "POST"
    action = "BatchGetDataset"
    service = "app"
    url_path = '/'

    # 1. เตรียม Body Data (Ids ต้องเป็น List)
    data = OrderedDict([
        ("Ids", dataset_ids), # ส่งเป็น ["id1", "id2"]
        ("WorkspaceID", workspace_id)
    ])
    print("BatchGetDataset Body Data:", data)
    # ใช้ separators เพื่อความเป๊ะของ Signature
    json_body = json.dumps(data, separators=(',', ':'))
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
        print("BatchGetDataset Response Status Code:", resp.status_code)
        print("BatchGetDataset Response:", resp.text)
        if resp.status_code != 200:
            print(f"BatchGetDataset API Error: {resp.text}")
            return None

        response_json = resp.json()
        return response_json.get("Result", {}).get("Items", []) # คืนค่าเป็น List ของ Dataset
    except Exception as e:
        print(f"BatchGetDataset Request failed: {e}")
        return None