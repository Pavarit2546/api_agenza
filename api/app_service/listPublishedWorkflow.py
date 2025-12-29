import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def list_published_workflows_service(creds, version, host, page_number, page_size, status_filter, workspace_id):
    """
    ลิสต์ workflow ที่ publish แล้วใน workspace ที่ระบุ
    """
    method = 'POST'
    action = 'ListPublishedWorkflow'
    service = 'app'
    url_path = '/' 

    # 1. เตรียม Body Data
    data = OrderedDict([
        ("ListOpt", {
            "PageNumber": int(page_number),
            "PageSize": int(page_size)
        }),
        ("Filter", {
            "StatusContain": status_filter
        }),
        ("WorkspaceID", str(workspace_id)),
        ("Top", {
            "DestService": service, # หรือตัวแปร service
            "DestAction": action # หรือตัวแปร action
        })  
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
    
    print("Requesting ListPublishedWorkflow URL:", url)
    print("Request Body:", json_body)
    
    try:
        resp = requests.request(method, url=url, headers=headers, data=json_body, verify=True, timeout=60)
        print("Response Status Code:", resp.status_code)
        print("Response Text:", resp.text)
        response_json = resp.json()
        
        if resp.status_code != 200:
            error_info = response_json.get("ResponseMetadata", {}).get("Error", {})
            return {
                "error": True,
                "status": resp.status_code,
                "message": error_info.get("Message", "ListPublishedWorkflow failed")
            }

        return {"status": 200, "message": response_json.get("Result")}

    except Exception as e:
        return {"error": True, "status": 500, "message": str(e)}