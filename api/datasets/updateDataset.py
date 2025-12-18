# api/createDataset.py
import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def update_dataset_service(name, workspace_id, dataset_id, desc, creds, version, host):
    method = "POST"
    action = "UpdateDataset"
    service = "app"
    url_path = '/'

    # 1. เตรียม Body Data ตามเอกสาร
    data = {
        "Name": name,
        "Id":dataset_id,
        "WorkspaceID": workspace_id,
        "Description":  desc,
        "DirectoryID": "default", 
        "SpaceType": 1,
    }
    
    print("updateDataset Body Data:", data)
    json_body = json.dumps(data)
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()
    print("updateDataset Body Hash:", body_hash)
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
    print("updateDataset URL:", url)

    try:
        resp = requests.request(method, url=url, headers={'Content-Type': 'application/json'}, data=json_body, verify=True, timeout=30)
        if resp.status_code == 400:
            print("DEBUG SERVER RESPONSE:", resp.text)
        resp.raise_for_status()
        print("UpdateDataset Response:", resp.text)
        return True # ผลลัพธ์ Result เป็น {} แสดงว่าสำเร็จ
    except Exception as e:
        print(f"Update Error: {e}")
        return False