from dataclasses import dataclass
from typing import List
from mongoengine.document import *
from mongoengine.fields import *
from mongoengine import *


try:
    import json
    import os
    db_auth = json.loads(os.environ["DBAUTH"])
except:
    from dotenv import load_dotenv
    load_dotenv()
    db_auth = json.loads(os.environ["DBAUTH"])


connect(**db_auth)
class Tokens(Document):
    refresh = StringField(primary_key=True)
    auth = StringField()
    
from pydantic import BaseModel


class UserBaseModel(BaseModel):
    id: int
    name: str
    account: str = ''

class TagBaseModel(BaseModel):
    name: str

class ImageUrlBaseModel(BaseModel):
    large: str
    # medium: str
    # square_medium: str


class PendingBaseModel(BaseModel):
    id: int
    title: str
    user: UserBaseModel
    tags: List[TagBaseModel]
    create_date: str
    total_view: int
    total_bookmarks: int
    x_restrict: int # 0:正常，1:R-18，2:R-18G



class Pending(Document):
    """爬虫自己准备好的图"""
    id = IntField(primary_key=True)
    title = StringField()
    user = DictField()
    tags = ListField(DictField())
    create_date = StringField()
    total_view = IntField()
    total_bookmarks = IntField()
    x_restrict = IntField()
    image_urls = DictField()

class Passed(Document):
    """我觉得可以放进api的图"""
    id = IntField(primary_key=True)
    typ = StringField() # 人工索引分类用，暂时想分R-18、艺术、色色
    title = StringField()
    user = DictField()
    tags = ListField(DictField())
    create_date = StringField()
    total_view = IntField()
    total_bookmarks = IntField()
    x_restrict = IntField()
    image_urls = DictField()

class Refused(Document):
    """我觉得不行的图"""
    id = IntField(primary_key=True)



from mongoengine.queryset.base import *

class PictureBinary(Document):
    id = ReferenceField(Pending, reverse_delete_rule=DO_NOTHING, primary_key=True)
    content = ImageField() # 必须手动删除，不能级联
