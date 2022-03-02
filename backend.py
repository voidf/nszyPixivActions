from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import *
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

import os
import sys

from datamodel import *

sys.dont_write_bytecode = True


app = FastAPI(version="1.0.0", title="setu evaluate system")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/bin/{pid}')
async def get_binary(pid:int):
    r = PictureBinary.objects(pk=pid).first()
    if r:
        return Response(r.content.read(), media_type='image/jpeg')
    else:
        raise HTTPException(404)

@app.get('/pending/{pid}')
async def get_pending(pid:int):
    r = Pending.objects(pk=pid).first()
    if r:
        return r.to_dict()
    else:
        raise HTTPException(404)

@app.get('/pendinglist')
async def get_pending_list(page: int=0, perpage: int=20):
    r = Pending.objects()[page*perpage:(page+1)*perpage]
    return json.loads(r.to_json())

@app.post('/pending/{pid}')
async def pass_pending(pid:int, typ:str):
    r = Pending.objects(pk=pid).first()
    if r:
        Passed(typ=typ, **r.get_all_info()).save()
        r.delete()
        return True
    else:
        raise HTTPException(404)

@app.delete('/pending/{pid}')
async def refuse_pending(pid:int):
    r = Pending.objects(pk=pid).first()
    if r:
        Refused(pk=pid).save()
        rb=PictureBinary.objects(pk=pid).first()
        rb.content.delete()
        rb.delete()
        r.delete()
        return True
    else:
        raise HTTPException(404)

# @app.on_event('startup')
# async def startup_coroutines():

import os
# import shlex
@app.get('/build/{b:path}')
async def file_proxy(b):
    if '..' in b:
        raise HTTPException(403, {'msg': '老师傅行行好别打了= ='})
    file_path = f'{os.getcwd()}/{b.replace("..","")}'
    print(file_path)
    if not os.path.exists(file_path):
        raise HTTPException(404)
    return FileResponse(file_path)


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    import uvicorn
    uvicorn.run(
        app,
        host='localhost',
        port=11001,
    )
