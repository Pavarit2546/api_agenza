import json
import hashlib
import requests
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def get_download_key(file_path_obs, client_id, creds, version, host) -> str:
    """
    Step 1: ยิงไปที่ /up/DownloadKey เพื่อขอ Key สำหรับดาวน์โหลด
    """
    method = "POST"
    action = "DownloadKey"
    service = "up"
    url_path = '/up/'

    # 1. เตรียม Body (เป็น JSON ว่างตาม curl)
    data = {}
    json_body = json.dumps(data)
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

    # 2. เตรียม Query Parameters (ต้องใส่ Path ไฟล์ที่ต้องการโหลด)
    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version
    query['Path'] = file_path_obs # เช่น upload/full/...
    query['Id'] = client_id

    # 3. เตรียม SignerV4
    sign = SignerV4()
    param = SignParam()
    param.path = url_path
    param.method = method
    param.host = host
    param.body = body_hash
    param.query = query
    
    header = OrderedDict()
    header['Host'] = host
    param.header_list = header

    # 4. Sign
    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)
    use_https = True
    
    url = f"{'https' if use_https else 'http'}://{host}{url_path}?{resulturl}"
    headers = {'Content-Type': 'application/json'}

    try:
        resp = requests.post(url, headers=headers, data=json_body, timeout=10)
        resp.raise_for_status()
        res_json = resp.json()
        
        # ดึง Key ออกมาจาก Result
        if res_json.get("ResponseMetadata", {}).get("Error") is None:
            return res_json.get("Result", {}).get("Key")
        return None
    except Exception as e:
        print(f"Get DownloadKey failed: {e}")
        return None