import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def get_document(doc_id, dataset_id, workspace_id, creds, version, host) -> dict:

    method = "POST"
    action = "GetDocument"
    service = "app"
    url_path = '/'
    
    # 1. เตรียม Body
    data = {
        "DatasetId": dataset_id,
        "Id": doc_id,  
        "WorkspaceID": workspace_id,
    }
    
    json_body = json.dumps(data)
    # [สำคัญ] คำนวณ Hash ของ Body จริงสำหรับการลงลายเซ็น
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()
    
    # 2. เตรียม Query Parameters
    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version
    
    # 3. เตรียม SignerV4 parameters
    sign = SignerV4()
    param = SignParam()
    param.path = url_path
    param.method = method
    param.host = host
    param.body = body_hash  # <--- ใช้ Hash ของ Body จริง
    param.query = query
    
    header = OrderedDict()
    header['Host'] = host
    param.header_list = header

    # 4. ลงลายเซ็น (Sign)
    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)
    use_https = True

    # 5. สร้าง URL และส่ง Request
    url = f"{'https' if use_https else 'http'}://{host}{url_path}?{resulturl}"
    headers = {'Content-Type': 'application/json'}
    print("url", url)

    try:
        resp = requests.request(method, url=url, headers=headers, data=json_body, verify=True, timeout=30)
        resp.raise_for_status()
        response_json = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"GetDocument Request failed: {e}")
        return None
    except json.JSONDecodeError:
        print("GetDocument failed: Invalid JSON response.")
        return None

    if response_json.get("ResponseMetadata", {}).get("Error") is None:
        return response_json.get("Result", {})
        # return response_json.get("Result", {}).get("Document", {})
    else:
        error_code = response_json.get('ResponseMetadata', {}).get('Error', {}).get('Code')
        error_msg = response_json.get('ResponseMetadata', {}).get('Error', {}).get('Message')
        print(f"GetDocument Failed. Server Error: Code={error_code}, Message={error_msg}")
        return None