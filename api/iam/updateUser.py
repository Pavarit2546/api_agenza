import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def update_user_service(creds, version, host, user_id, display_name, email, 
                        mobile, icon, description, org_ids, 
                        role_name, user_group_ids, username):
    method = "POST"
    action = "UpdateUser"
    service = "iam"
    url_path = '/api/iam'

    # 1. เตรียม Body Data (ใช้ค่าตามที่ส่งมาจาก Controller)
    data = OrderedDict([
        ("ID", str(user_id)),
        ("DisplayName", str(display_name)),
        ("Email", str(email)),
        ("Mobile", str(mobile)),
        ("Icon", str(icon)),
        ("Description", str(description)),
        ("OrgIDs", org_ids if org_ids else []),
        ("RoleName", str(role_name)),
        ("UserGroupIDs", user_group_ids if user_group_ids else []),
        ("UserName", str(username)),
        ("Top", {
            "DestService": service,
            "DestAction": action
        })
    ])

    json_body = json.dumps(data, separators=(',', ':'))
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

    # 2. ลงลายเซ็น V4
    sign = SignerV4()
    param = SignParam()
    param.path = url_path
    param.method = method
    param.host = host
    param.body = body_hash
    
    # เตรียม Query Parameters
    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version
    param.query = query


    header = OrderedDict()
    header['Host'] = host
    header['service'] = service
    param.header_list = header

    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)
    
    # 3. สร้าง URL สุดท้าย
    url = f"https://{host}{url_path}?{resulturl}"
    
    print("Requesting CreateUser URL:", url)
    print("Body Data:", json_body)

    try:
        headers = {
            'Content-Type': 'application/json',
            'service': service,
            'X-Top-Dest-Service': service,
            'X-Top-Dest-Action': action,
        }
        
        resp = requests.request(method, url=url, headers=headers, data=json_body, verify=True)
        response_data = resp.json()
        print("response_data:", response_data)
    
        if resp.status_code != 200:
            error_info = response_data.get("ResponseMetadata", {}).get("Error", {})
            return {
                "error": True,
                "status": resp.status_code,
                "message": error_info.get("Message", "Update failed")
            }

        return {"error": False, "status": 200, "data": response_data.get("Result")}

    except Exception as e:
        return {"error": True, "status": 500, "message": str(e)}