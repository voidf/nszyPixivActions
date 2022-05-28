from datamodel import *
import json
import os
d = r'C:\Users\ATRI\Desktop\liandan\photos'
for i in OtherSourcePicture.objects():
    i.content.delete()
    i.delete()

for i in os.listdir(d):
    with open(d+'/'+i, 'rb') as f:
        o = OtherSourcePicture(category='exh')
        o.content.put(f)
        o.save()
