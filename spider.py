import requests
from pixivpy3 import *
import json
import sys
sys.dont_write_bytecode = True
from datamodel import *

_REQUESTS_KWARGS = {
    'proxies': {
        'https': 'http://127.0.0.1:7890',
        'http': 'http://127.0.0.1:7890',
    },
    # 'verify': False,       # PAPI use https, an easy way is disable requests SSL verify
}

# download_session = requests.Session()
# download_session.headers = {
#     'Referer':'https://www.pixiv.net/'
# }



api = AppPixivAPI(**_REQUESTS_KWARGS)
api.auth(refresh_token=Tokens.objects().first().refresh)
import traceback
def get_illust_follow_new(debug=False) -> list:
    tot = []
    j = api.illust_follow()
    tot.extend(j.illusts)
    if not debug:
        nxt = api.parse_qs(j.next_url)
        import time
        import random
        try:
            while nxt is not None:
                j = api.illust_follow(**nxt)
                print(str(j)[:100])
                tot.extend(j.illusts)
                nxt = api.parse_qs(j.next_url)
                time.sleep(random.randint(3,7))

                with open('tmp.json','w') as f:
                    json.dump(tot, f)
        except:
            traceback.print_exc()
            with open('tmp.json','r') as f:
                tot = json.load(f)
    return tot

def recover_from_disk():
    with open('tmp.json','r') as f:
        tot = json.load(f)
    if isinstance(tot, dict):
        tot = tot['illusts']
    return tot

def get_promoted():
    # if not Promoted.objects():
        # Promoted(pk=84019281).save()
        # Promoted(pk=68419907).save()

    res = []

    for i in Promoted.objects():
        if PictureBinary.objects(pk=i.pk) or Refused.objects(pk=i.pk) or Passed.objects(pk=i.pk):
            print(f'found {i} already in database.')
        else:
            detail = api.illust_detail(i.pk)
            res.append(detail.illust)
        
        i.delete()
    return res


def download_pictures(tot: list):
    from io import BytesIO
    content = BytesIO()
    for ind,i in enumerate(tot):
        if PictureBinary.objects(pk=i['id']) or Refused.objects(pk=i['id']) or Passed.objects(pk=i['id']):
            if ind % 100 == 0:
                print(f'skipped ({ind+1}/{len(tot)})')
            continue
        model = PendingBaseModel.parse_obj(i)
        p = Pending(**model.dict()).save()
        try:
            api.download(i['image_urls']['large'], fname=content)
            b = PictureBinary(id=p)
            b.content.put(content)
            b.save()
        except:
            traceback.print_exc()
        finally:
            print(f'downloading ({ind+1}/{len(tot)}) pid={i["id"]}')
            content.truncate(0)
            content.seek(0)

# get_promoted()

# Pending.objects().delete()
download_pictures(get_illust_follow_new() + get_promoted())
print('Done work')
    # with open('tmp.json', 'r') as f:
    #     j = json.load(f)
    #     li = j['illusts']
    #     for i in li:
    #         i['_id'] = i.pop('id')
    
    # with open('tmp2.json','w') as ff:
        # json.dump(li, ff)


