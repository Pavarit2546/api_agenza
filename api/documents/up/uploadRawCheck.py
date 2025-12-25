import json
import hashlib
import requests
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def upload_raw_file(file_path, workspace_id, client_id, creds, version, host) -> str:
    
    method = "POST"
    action = "UploadRawCheck"
    service = "up"

    # 1. อ่านไฟล์และคำนวณ SHA256 Hash
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
    except FileNotFoundError:
        return None # Return None on failure
        
    sha256_hash = hashlib.sha256(file_data).hexdigest()
    
    # 2. เตรียม URL Path
    url_path = f'/up/'

    # 3. เตรียม Query Parameters
    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version
    query['Id'] = client_id
    query['X-Account-Id'] = workspace_id

    # 4. เตรียม Header
    headers = {
        "Content-Type": "application/json", 
        "X-Content-Sha256": sha256_hash,
    }

    # 5. เตรียม SignerV4 parameters
    sign = SignerV4()
    param = SignParam()
    param.path = url_path
    param.method = method
    param.host = host
    param.body = sha256_hash
    param.query = query
    
    header = OrderedDict()
    header['Host'] = host
    param.header_list = header

    # 6. ลงลายเซ็น (Sign)
    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)
    use_https = True
    
    # 7. สร้าง URL และส่ง Request
    url = f"{'https' if use_https else 'http'}://{host}{url_path}?{resulturl}"
    
    # [สำคัญ] ส่งข้อมูลไฟล์ไบนารีตรง ๆ (file_data)
    try:
        response = requests.request(
            method, 
            url=url, 
            headers=headers, 
            data=file_data,
            verify=True,
            timeout=30
        )
        response.raise_for_status()
        response_json = response.json()
        print("Response Status Code:", response.status_code)
        print("Response Body:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Cannot decode JSON. Status: {response.status_code}")
        return None

    if response_json.get("ResponseMetadata", {}).get("Error") is None:
        obs_url = response_json.get("Result", {}).get("Path")
        return obs_url
    else:
        print(f"Upload Raw Failed. Status Code: {response.status_code}")
        return None

