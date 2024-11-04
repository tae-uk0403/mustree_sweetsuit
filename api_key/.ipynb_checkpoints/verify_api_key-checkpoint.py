
from fastapi import FastAPI, File, UploadFile, Query, Body, status, Request, Response, Depends, HTTPException, Header
from datetime import datetime
import logging
import json


def verify_api_key(api_key: str = Header(...)):
    
    logging.basicConfig(filename='app.log', level=logging.INFO)    
    
    valid_api_keys = []
    info_dir = 'api_key/api_info.json'
    with open(info_dir, 'r', encoding='utf-8') as file:
            data = json.load(file)
    for info in data['info']:
        valid_api_keys.append(info.get("key"))
    
    if api_key not in valid_api_keys:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    return api_key