import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def publish_app_service(    creds, version, host, preprompt, temperature, topP, 
    maxtokens, tool_ids, workflow_ids, workflow_version, 
    knowledge_ids, qa_dataset_ids, database_ids, 
    workspace_id, app_id,
    workflow_publish_id, workflow_id=None):
    """
    Publish App ใน workspace ที่ระบุ
    """
    method = "POST"
    action = "PublishAppV2"
    service = "app"
    url_path = '/'
    # 1. เตรียม Body Data
    data = OrderedDict([
        ("AppID", str(app_id)),
        ("WorkspaceID", str(workspace_id)),
        ("AgentMode", "Single"), # หรือรับจาก req_data.get("agent_mode", "Single")
    ])

    data["AppConfig"] = {
        "ModelID": "d393no652vvc73d72a20",
        "ModelConfig": {
            "Temperature": temperature,
            "TopP": topP,
            "MaxTokens": maxtokens,
            "RoundsReserved": 3,
            "RagNum": 3,
            "Strategy": "react",
            "MaxIterations": 5,
            "RagEnabled": False,
            "ReasoningSwitchType": "disabled",
            "ReasoningMode": False,
            "CurrentTimeEnabled": False,
            "ReasoningSwitch": False
        },
        "SummaryModelID": "",
        "PrePrompt": preprompt if not workflow_id else "", # ถ้าเป็น workflow อาจจะไม่เน้น prompt ตรงนี้
        "PromptConfig": {"PromptMode": "regex"},
        "VariableConfigs": [],
        "ToolIDs": tool_ids,
        "WorkflowIDs": workflow_ids,
        "KnowledgeIDs": knowledge_ids,
        "QADatasetIDs": qa_dataset_ids,
        "DatabaseIDs": database_ids,
        "KnowledgeConfig": {"RetrievalSearchMethod": 0, "MatchType": "force", "TopK": 3, "Similarity": 0.5},
        "QADatasetConfig": {"RetrievalSearchMethod": 0, "MatchType": "force", "TopK": 1, "Similarity": 0.5},
        "ChatAdvancedConfig": {
            "UploadConfig": {
                "Enabled": True,
                "UploadDocumentAllowed": True,
                "UploadImageAllowed": True,
                "UploadAudioAllowed": True,
                "UploadVideoAllowed": True,
                "UploadCompressedAllowed": False
            },
            "OpeningConfig": {"OpeningQuestions": [], "OpeningEnabled": False},
            "SuggestEnabled": False,
            "ReferenceEnabled": False,
            "ReviewEnabled": False,
            "SuggestPromptConfig": {"Prompt": "", "Enabled": False},
            "AdvancedReviewType": "unused",
            "SpeechInteractionConfig": {},
            "ThoughtLanguageConfig": {"Language": "th"}
        },
        "GraphIDs": [],
        "GraphConfig": {"MatchType": "force", "SearchDepth": 3, "SearchType": 2, "TopK": 30},
        "TerminologyIDs": [],
        "TerminologyConfig": {"RetrievalSearchMethod": 0, "MatchType": "force", "TopK": 3, "Similarity": 0.5},
        "Version": "v1.0"
    }

    # --- 3. เพิ่ม ChatFlowConfig เฉพาะเมื่อมี workflow_id ---
    if workflow_id:
        data["ChatFlowConfig"] = {
            "WorkflowID": workflow_id,
            "WorkflowPublishID": workflow_publish_id,
            "Version": workflow_version,
            "ChatAdvancedConfig": {
                "SpeechInteractionConfig": {},
                "ThoughtLanguageConfig": {"Language": "th"}
            }
        }

    # --- 4. ส่วน Channels และ Publish Settings ---
    data["BuiltinChannels"] = ["api", "mcp", "web", "websdk"]
    data["CustomChannels"] = []
    data["WebAccessConfig"] = {"AccessType": "Public"}
    data["PublishWx"] = {"IsPublish": False}
    data["PublishAppCenter"] = {"IsPublish": False}
    data["PublishLark"] = {"IsPublish": False}
    data["PublishThirdparty"] = []

    # --- 5. ส่วนท้ายสุด ---
    data["Top"] = {
        "DestService": service,
        "DestAction": action
    }

    json_body = json.dumps(data)
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
    
    print("Requesting PubilshApp URL:", url)
    print("Body Data:", json_body)

    try:
        headers = {
            'Content-Type': 'application/json',
            'X-Top-Dest-Service': service,
            'X-Top-Dest-Action': action,
        }
        
        resp = requests.request(method, url=url, headers=headers, data=json_body, verify=True)
        
        # แสดงผลลัพธ์เพื่อ Debug
        print(f"Response Status: {resp.status_code}")
        print(f"Response Text: {resp.text}")
        
        response_data = resp.json()

        if resp.status_code != 200:
            error_info = response_data.get("ResponseMetadata", {}).get("Error", {})
            return {
                "error": True,
                "status": resp.status_code,
                "message": error_info.get("Message", "Delete failed"),
                "data": error_info.get("Data", {})
            }

        return {"error": False, "status": 200, "message": response_data.get("Result")}

    except Exception as e:
        return {"error": True, "status": 500, "message": str(e)}