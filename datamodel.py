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

from typing import *

INVISIBLE = TypeVar('INVISIBLE')

class Base():
    """需要和mongoengine的Document多继承配套使用"""
    @staticmethod
    def expand_mono(obj):
        if hasattr(obj, 'get_base_info'):
            return getattr(obj, 'get_base_info')()
        else:
            return obj
    def get_base_info(self, *args):
        try:
            d = {}
            for k in self._fields_ordered:
                if get_type_hints(self).get(k, None) == INVISIBLE:
                    continue
                selfk = getattr(self, k)
                if isinstance(selfk, list):
                    for i in selfk:
                        d.setdefault(k, []).append(Base.expand_mono(i))
                else:
                    d[k] = Base.expand_mono(selfk)
            d['id'] = str(self.id)
            return d
        except: # 不加注解上面会报错
            return self.get_all_info()
    def get_all_info(self, *args):
        d = {} 
        for k in self._fields_ordered:
            selfk = getattr(self, k)
            if isinstance(selfk, list):
                for i in selfk:
                    d.setdefault(k, []).append(Base.expand_mono(i))
            else:
                d[k] = Base.expand_mono(selfk)
        if hasattr(self, 'id'):
            d['id'] = str(self.id)
        return d
    @classmethod
    def chk(cls, pk):
        """确保对象存在，如不存在则创建一个，返回给定主键确定的对象"""
        if isinstance(pk, cls):
            return pk
        tmp = cls.objects(pk=pk).first()
        if not tmp:
            return cls(pk=pk).save()
        return tmp
    @classmethod
    def trychk(cls, pk):
        """若对象存在，返回主键对应的对象，否则返回None"""
        if isinstance(pk, cls):
            return pk
        tmp = cls.objects(pk=pk).first()
        if not tmp:
            return None
        return tmp
    
    def to_dict(self):
        return json.loads(self.to_json())

class SaveTimeBase(Base):
    create_time = DateTimeField()
    def save_changes(self):
        return self.save()
    def first_create(self):
        self.create_time = datetime.datetime.now()
        return self.save_changes()
    
    def get_base_info(self, *args):
        d = super().get_base_info(*args)
        d['create_time'] = self.create_time.strftime('%Y-%m-%d')
        return d

    def get_all_info(self, *args):
        d = super().get_all_info(*args)
        d['create_time'] = self.create_time.strftime('%Y-%m-%d')
        return d





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

class Promoted(Document):
    """我知道pixiv id想加的图"""
    id = IntField(primary_key=True)

class Pending(Document, Base):
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
    typ = StringField() # 人工索引分类用，暂时想分R-18、好看、色色、帅哥
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
