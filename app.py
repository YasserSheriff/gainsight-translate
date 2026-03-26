import json
import os
import re
import sys
import time
import uuid
import uvicorn
import requests
from langchain_text_splitters import RecursiveCharacterTextSplitter

from datetime import datetime, timedelta

from dotenv import load_dotenv

# Fast API
from fastapi import FastAPI, Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.middleware.cors import CORSMiddleware


# Custom type classes
from customTypes.langcheckRequest import langcheckRequest
from customTypes.langcheckResponse import langcheckResponse
from customTypes.translateRequest import translateRequest
from customTypes.translateResponse import translateResponse

app = FastAPI()

# Set up CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
# APP Security
API_KEY_NAME = "APP_API_KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Token to IBM Cloud
ibm_cloud_api_key = os.environ.get("IBM_CLOUD_API_KEY")
project_id = os.environ.get("WX_PROJECT_ID")
wx_langcheck_url = os.environ.get("WX_LANGCHECK_URL")
wx_translate_url = os.environ.get("WX_TRANSLATE_URL")

token_updated_at = None
token = None
headers = None


def get_auth_token(api_key):
    auth_url = "https://iam.cloud.ibm.com/identity/token"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    response = requests.post(auth_url, headers=headers, data=data, verify=False)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Failed to get authentication token")


def update_token_if_needed(api_key):
    global token, token_updated_at, headers
    if token is None or datetime.now() - token_updated_at > timedelta(minutes=20):
        print(f'updating token')
        token =  get_auth_token(api_key)
        token_updated_at = datetime.now()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }


# Basic security for accessing the App
async def get_api_key(api_key_header: str = Security(api_key_header)):
    print(api_key_header)
    print(os.environ.get("APP_API_KEY"))
    if api_key_header == os.environ.get("APP_API_KEY"):
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate APP credentials. Please check your ENV."
        )

@app.get("/")
def index():
    return {"IBM": "Build Engineering"}


@app.post("/langcheck")
async def langcheck(request: langcheckRequest, api_key: str = Security(get_api_key)):
    print("Request: " + request.text)
    text = request.text

    nlrequest ={"parameters": 
        { 
            "prompt_variables": { "text": text } 
        } 
    }
    nlResponse = {}
    try:
       lang_check_response = watsonx (wx_langcheck_url, nlrequest)
    except Exception as e:
      nlResponse['error'] = str(e)

    match = re.search(r"\{([\s\S]*?)\}", lang_check_response)
    if match:
        json_output = json.loads("{"+match.group(1).strip()+"}")
        print(json_output)  

    return langcheckResponse(response=json_output)


@app.post("/translate")
async def langcheck(request: translateRequest, api_key: str = Security(get_api_key)):
    
    nlResponse = {}
    try:            
        print("Request: " + request.text)
        text = request.text

        # txt_chunks = text.split("\n")
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=15000, 
            chunk_overlap=0,
            separators=["\n\n", "\n", ". ", "。", "！", "？"]
        )

        txt_chunks = splitter.split_text(text)
        
        print("\n\n||> Len",len(txt_chunks))

        translated_chunk = ""
        # Language_chunk = ""

        for chunk in txt_chunks:
            print(chunk)    
            nlrequest ={"parameters": 
                { 
                    "prompt_variables": { "text": chunk } 
                } 
            }
            translate_response = watsonx(wx_translate_url, nlrequest)
            generated_token_count = translate_response['results'][0]["generated_token_count"]
            input_token_count = translate_response['results'][0]["input_token_count"]

            print("translate_response")
            print(translate_response)
            match = re.search(r"\{([\s\S]*?)\}", translate_response.get("results")[0].get("generated_text"))
            if match:
                json_output = json.loads("{"+match.group(1).strip()+"}")
                translated_chunk += json_output.get("Translation") #+"\n"
                Language_chunk = json_output.get("Language")
                print("\nLanguage_chunk\n\n",translated_chunk,"\n\nLanguage_chunk\n")
                
        return translateResponse(response={"Translation":translated_chunk, "Language": Language_chunk, "input_token_count": input_token_count, "generated_token_count": generated_token_count, "request_id": uuid.uuid4(), "timestamp": int(time.time() * 1000)})
    
    except Exception as e:
        nlResponse['error'] = str(e)
        return nlResponse
    
#@app.post("/watsonx")
def watsonx(deployment, payload):
    
    #iam_token = get_auth_token(os.getenv("IBM_CLOUD_API_KEY", None))
    
    update_token_if_needed(os.getenv("IBM_CLOUD_API_KEY", None))

    response = requests.post(deployment, headers=headers, json=payload, verify=False).json()
    print("RESPONSE : " + str(response))
    message = response['results'][0]['generated_text']
    print(response['results'][0]["generated_token_count"])
    print(" message: " + str(message))
    return response


if __name__ == '__main__':
    if 'uvicorn' not in sys.argv[0]:
        uvicorn.run("app:app", host='0.0.0.0', port=4050, reload=True)