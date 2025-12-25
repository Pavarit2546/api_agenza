import json
import requests
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def list_app_center(creds, version, host) -> list:
    
    method = 'POST'
    action = 'ListAppCenter'
    service = 'app'
    url_path = '/' 

    # 1. เตรียม Query Parameters
    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version
    
    # 2. เตรียม Body
    data = {"App": True}
    json_body = json.dumps(data)
    param_body_value = ''
    
    # 3. เตรียม SignerV4 parameters
    sign = SignerV4()
    param = SignParam()
    param.path = url_path
    param.method = method
    param.host = host
    param.body = param_body_value
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
        print(f"!!! Final Request failed (Network/Timeout): {e}")
        return []
    except json.JSONDecodeError:
        print(f"!!! Final Request failed (JSON Decode Error): Response was not valid JSON.")
        return []

    if response_json.get("ResponseMetadata", {}).get("Error") is None:
        return response_json.get("Result", {}).get("Items", [])
    else:
        error_code = response_json.get('ResponseMetadata', {}).get('Error', {}).get('Code')
        error_msg = response_json.get('ResponseMetadata', {}).get('Error', {}).get('Message')
        print(f"List App Failed. Server Error: Code={error_code}, Message={error_msg}")
        return []

