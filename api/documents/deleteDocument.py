import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def delete_document(doc_id, dataset_id, workspace_id, creds, version, host) -> list:
    
    method = 'POST'
    action = 'DeleteDocument'
    service = 'app'
    url_path = '/' 
    data = {
        "DatasetId": dataset_id,
        "Id": doc_id,
        "WorkspaceID": workspace_id,
    }
    json_body = json.dumps(data)
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()
    
    # 1. เตรียม Query Parameters
    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version
    
    
    # 3. เตรียม SignerV4 parameters
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

    # 4. ลงลายเซ็น (Sign)
    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)
    use_https = True

    # 5. สร้าง URL และส่ง Request
    url = f"{'https' if use_https else 'http'}://{host}{url_path}?{resulturl}"
    headers = {'Content-Type': 'application/json'}
    print("url", url)
    
    try:
        resp = requests.request(method, url=url, headers=headers, data=json_body, verify=True, timeout=60)
        resp.raise_for_status()
        response_json = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"!!! Delete Document Request failed (Network/Timeout): {e}")
        return False
    except json.JSONDecodeError:
        if resp.status_code == 200:
             return True
        print("!!! Delete Document failed (JSON Decode Error): Response was not valid JSON.")
        return False

    if response_json.get("ResponseMetadata", {}).get("Error") is None:
        return True 
    else:
        error_code = response_json.get('ResponseMetadata', {}).get('Error', {}).get('Code')
        error_msg = response_json.get('ResponseMetadata', {}).get('Error', {}).get('Message')
        print(f"Delete Document Failed. Server Error: Code={error_code}, Message={error_msg}")
        return False

