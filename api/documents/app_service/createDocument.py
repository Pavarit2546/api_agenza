import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def create_document(obs_url, workspace_id, filename, creds, version, host, dataset_id, doc_name) -> str:
    
    method = "POST"
    action = "CreateDocument"
    service = "app"
    url_path = '/'

    # 1. เตรียม Body
    # [สำคัญ] ข้อมูลใน Body ที่คุณให้มาถูกใช้ในการลงลายเซ็นด้วย
    data = {
        "DatasetId": dataset_id,
        "DocumentLabels": [
            {"Description": "test", "EnableFilter": True, "Name": doc_name, "Type": 0, "Value": "jjj"}
        ],
        "NormalDocuments": [
            {
                "CronRule": "", "EnableImageParse": False, "EnablePageAnalysis": True, 
                "EnableSegmentIndex": True, "EnableSegmentQuestion": False, 
                "Filename": filename,
                "ObsUrl": obs_url,
                "ProcessRule": 0, "ProcessRuleChunkOverlap": 0, "ProcessRuleChunkSize": 1000, 
                "ProcessRuleDelimiter": "\n\n", "ProcessRuleEnableOcr": False, 
                "ProcessRuleEnableSemantic": False, "ProcessRuleRemoveExtraSpace": False, 
                "ProcessRuleRemoveReferences": False, "ProcessRuleRemoveURLEmail": False, 
                "SegmentWithFilename": False, "SegmentWithTitle": False, "Type": 0,
                "Url": obs_url
            }
        ],
        "ProcessRuleFileType": 0,
        "WorkspaceID": workspace_id
    }
    json_body = json.dumps(data)
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
    use_https = True

    # 5. สร้าง URL และส่ง Request
    url = f"{'https' if use_https else 'http'}://{host}{url_path}?{resulturl}"

    headers = {'Content-Type': 'application/json'}

    try:
        resp = requests.request(method, url=url, headers=headers, data=json_body, verify=True, timeout=30)
        resp.raise_for_status()
        response_json = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    if response_json.get("ResponseMetadata", {}).get("Error") is None:
        doc_ids = response_json.get("Result", {}).get("Ids", [])
        return doc_ids[0] if doc_ids else None
    else:
        print(f"Create Document Failed. Status Code: {resp.status_code}")
        return None

