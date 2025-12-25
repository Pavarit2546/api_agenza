import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def create_app_service(creds, version, host, workspace_id, name, description, app_type):
    """
    สร้างแอปใหม่ใน App Center
    """
    method = 'POST'
    action = 'CreateApp'
    service = 'app'
    url_path = '/' 

    # 1. เตรียม Body Data
    data = OrderedDict([
        ("WorkspaceID", str(workspace_id)),
        ("Name", str(name)),
        ("AppType", str(app_type)),
        ("Description", str(description)),
        ("Icon", ""),
        ("Background", ""),
        ("WorkflowIDs", []),
        ("Top", {})
    ])

    json_body = json.dumps(data, separators=(',', ':'))
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
    param.body = body_hash
    param.query = query

    header = OrderedDict()
    header['Host'] = host
    param.header_list = header

    # 4. ลงลายเซ็น (Sign)
    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)

    # 5. สร้าง URL และส่ง Request
    url = f"https://{host}{url_path}?{resulturl}"
    headers = {
        'Content-Type': 'application/json',
    }
    
    print("Requesting CreateApp URL:", url)
    print("Request Body:", json_body)
    
    try:
        resp = requests.request(method, url=url, headers=headers, data=json_body, verify=True, timeout=60)
        print("Response Status Code:", resp.status_code)
        print("Response Text:", resp.text)
        response_json = resp.json()
        
        if response_json.get("ResponseMetadata", {}).get("Error") is None:
            print("Create App Success!")
            return response_json.get("Result")
        else:
            error = response_json.get("ResponseMetadata", {}).get("Error")
            print(f"Create App Failed: {error.get('Code')} - {error.get('Message')}")
            return None

    except Exception as e:
        print(f"Request failed: {e}")
        return None