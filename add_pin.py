#!/usr/bin/env python3
"""Append a daily pin item to an RSS board feed, then rebuild.
Usage: python3 add_pin.py --listing 4593692171 --board wedding-welcome-signs --image /path/pin.png --title "..." --desc "..."
Boards: event-planner-templates, wedding-welcome-signs, norwegian-wall-art, bridal-shower"""
import argparse,json,os,datetime,shutil,subprocess
from PIL import Image
D=os.path.dirname(os.path.abspath(__file__))
a=argparse.ArgumentParser();[a.add_argument(f'--{k}',required=True) for k in ('listing','board','image','title','desc')];a=a.parse_args()
assert a.listing in {x['id'] for x in json.load(open(f'{D}/listings.json'))},'unknown listing'
assert a.board in ('event-planner-templates','wedding-welcome-signs','norwegian-wall-art','bridal-shower')
now=datetime.datetime.now().astimezone(); guid=f"pin-{now:%Y%m%d%H%M%S}-{a.listing}"
os.makedirs(f'{D}/docs/img/pins',exist_ok=True); rel=f'img/pins/{guid}.jpg'
im=Image.open(a.image).convert('RGB'); im.thumbnail((1000,1500)); im.save(f'{D}/docs/{rel}',quality=88)
f=f'{D}/pins.json'; pins=json.load(open(f)) if os.path.exists(f) else []
pins.append(dict(guid=guid,listing_id=a.listing,board=a.board,image=rel,title=a.title,desc=a.desc,date=now.isoformat()))
json.dump(pins,open(f,'w'),indent=1,ensure_ascii=False)
subprocess.run(['python3',f'{D}/build.py'],check=True); print('added',guid)
