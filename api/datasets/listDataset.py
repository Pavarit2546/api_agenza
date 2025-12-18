import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def list_dataset_service(workspace_id, creds, version, host) -> str:
    
    method = "POST"
    action = "ListDatasets"
    service = "app"
    url_path = '/'

    data = {
        "WorkspaceID": workspace_id,
    }
    
    print("Body Data:", data)
    json_body = json.dumps(data)
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()
    print("Body Hash:", body_hash)
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
    use_https = True

    # 5. สร้าง URL และส่ง Request
    url = f"{'https' if use_https else 'http'}://{host}{url_path}?{resulturl}"
    print("url", url)
    headers = {'Content-Type': 'application/json'}

    try:
        resp = requests.request(method, url=url, headers=headers, data=json_body, verify=True, timeout=30)
        print("Response Status Code:", resp.status_code)
        print("Response Body:", resp.text)
        resp.raise_for_status()
        response_json = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    if response_json.get("ResponseMetadata", {}).get("Error") is None:
        doc_ids = response_json.get("Result", {})
        return doc_ids
    else:
        print(f"list Dataset Failed. Status Code: {resp.status_code}")
        return None

