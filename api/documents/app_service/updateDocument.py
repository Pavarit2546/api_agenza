import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def update_document(doc_id, dataset_id, workspace_id, filename, creds, version, host) -> bool:
    method = "POST"
    action = "UpdateDocument"
    service = "app"
    url_path = '/'

    # 1. เตรียม Body Data
    # หมายเหตุ: เลือกอัปเดตเฉพาะค่าที่ส่งมา (Optional)
    data = {
        "WorkspaceID": workspace_id,
        "DatasetId": dataset_id,
        "Id":doc_id,
        "ProcessRuleFileType": 0,
        "Filename": filename,
        "NormalDocument": {     
            "ProcessRule": 0,
            "EnablePageAnalysis": True,
            "EnableSegmentIndex": True,
        }
    }
    print(f"DEBUG DATA SENT: {data}")

    json_body = json.dumps(data)
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

    # 2. SignerV4 Setup (เหมือนกับ Get/Delete/List)
    sign = SignerV4()
    param = SignParam()
    param.path = url_path
    param.method = method
    param.host = host
    param.body = body_hash
    param.query = OrderedDict([('Action', action), ('Version', version)])
    param.header_list = OrderedDict([('Host', host)])

    # 3. ลงลายเซ็นและส่ง Request
    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)
    url = f"https://{host}{url_path}?{resulturl}"
    print("UpdateDocument URL:", url)
    
    try:
        resp = requests.request(method, url=url, headers={'Content-Type': 'application/json'}, data=json_body, verify=True)
        if resp.status_code == 400:
            print("DEBUG SERVER RESPONSE:", resp.text)
        resp.raise_for_status()
        print("UpdateDocument Response:", resp.text)
        return True # ผลลัพธ์ Result เป็น {} แสดงว่าสำเร็จ
    except Exception as e:
        print(f"Update Error: {e}")
        return False