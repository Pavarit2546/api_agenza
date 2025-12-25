import json
import hashlib
import requests
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def download_file(file_path_obs, download_key, creds, version, host):
    """
    Step 2: ยิงไปที่ /down/Download พร้อมกับ Key ที่ได้มา
    """
    method = "POST"
    action = "Download"
    service = "up"
    url_path = '/up/'

    # 1. Body ว่าง
    data = {}
    json_body = json.dumps(data)
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

    # 2. Query Params (ต้องมี Path และ Key)
    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version
    query['Path'] = file_path_obs
    query['Key'] = download_key

    # 3. Sign
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

    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)
    use_https = True
    

    url = f"{'https' if use_https else 'http'}://{host}{url_path}?{resulturl}"
    headers = {'Content-Type': 'application/json'}

    try:
        resp = requests.post(url, headers=headers, data=json_body, stream=True, timeout=60)
        print("Download Status:", resp.status_code)
        if resp.status_code == 200:
            return resp  # คืนค่าเป็น Response Object
        else:
            print(f"Error: {resp.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None