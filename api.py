from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import *
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

import os
import sys

from datamodel import *

sys.dont_write_bytecode = True


app = FastAPI(version="1.0.0", title="setu randomize system")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/bin/{pid}')
async def get_binary(pid:int):
    """拿库里给定pid的一张图
    """
    r = PictureBinary.objects(pk=pid).first()
    if r:
        return Response(r.content.read(), media_type='image/jpeg')
    else:
        raise HTTPException(404)

@app.get('/pending/{pid}')
async def get_pending(pid:int):
    """拿待审区的图
    """
    r = Pending.objects(pk=pid).first()
    if r:
        return r.to_dict()
    else:
        raise HTTPException(404)

@app.get('/random')
async def get_pending_list(typ: str='ero'):
    """随机拿一条图的信息

    可以使用typ指定需要的种类：

    - kawaii
        萝莉涩图

    - ero
        默认涩图

    - nice
        完成度高的或者艺术感占主要成分的图

    - r18
        不带幻影坦克会炸群的图，可能不色但一定是黄图

    - kusa
        试试就逝世
    
    """
    r = Passed.objects().aggregate([{
        '$match': { 'typ': typ }
   },{
        '$sample':{'size':1}
    }])
    print(r)
    for i in r:
        # print(i)
        i['id'] = i.pop('_id')

        return i

@app.get('/randbin')
async def get_pending_list(typ: str='ero'):
    """随机拿一张图的二进制

    可以使用typ指定需要的种类：

    - kawaii
        萝莉涩图

    - ero
        默认涩图

    - nice
        完成度高的或者艺术感占主要成分的图

    - r18
        不带幻影坦克会炸群的图，可能不色但一定是黄图

    - kusa
        试试就逝世
    
    """
    r = Passed.objects().aggregate([{
        '$match': { 'typ': typ }
   },{
        '$sample':{'size':1}
    }])
    print(r)
    for i in r:
        return Response(PictureBinary.objects(pk=i['_id']).first().content.read(), media_type='image/jpeg')

if __name__ == '__main__':
    sys.dont_write_bytecode = True
    import uvicorn
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=11002,
    )
