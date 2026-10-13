#!/usr/bin/env python3
"""Build static PlanNest Studio pin site + per-board RSS feeds. Usage: python3 build.py
Set SITE_URL in config.json after GitHub account exists (e.g. https://USER.github.io)."""
import json, os, html, datetime, email.utils
from PIL import Image
D=os.path.dirname(os.path.abspath(__file__)); E='/workspace/etsy'
cfg=json.load(open(f'{D}/config.json')); SITE=cfg['site_url'].rstrip('/'); VERIFY=cfg.get('pinterest_verify','')
L=json.load(open(f'{D}/listings.json'))
BOARDS={'event-planner-templates':'Event Planner Templates','wedding-welcome-signs':'Wedding Welcome Signs',
 'norwegian-wall-art':'Norwegian Wall Art','bridal-shower':'Bridal Shower'}
os.makedirs(f'{D}/docs/img',exist_ok=True); os.makedirs(f'{D}/docs/p',exist_ok=True); os.makedirs(f'{D}/docs/feeds',exist_ok=True)
def img(src,name):
    out=f'{D}/docs/img/{name}.jpg'
    if not os.path.exists(out) or os.path.getmtime(out)<os.path.getmtime(src):
        im=Image.open(src).convert('RGB'); im.thumbnail((1000,1500)); im.save(out,quality=85)
    return f'img/{name}.jpg'
META=lambda: f'<meta name="p:domain_verify" content="{VERIFY}"/>' if VERIFY else '<!-- PINTEREST_VERIFY: put <meta name="p:domain_verify" content="..."/> here via config.json -->'
CSS='body{font-family:Georgia,serif;background:#111;color:#eee;margin:0;text-align:center}a{color:#d4af37}header{padding:20px}header img{height:80px}.g{display:flex;flex-wrap:wrap;justify-content:center;gap:16px;padding:16px}.c{width:260px;background:#1c1c1c;padding:10px;border-radius:8px}.c img{width:100%}.m{max-width:720px;margin:auto;padding:16px}.m img{max-width:100%}.b{display:inline-block;background:#d4af37;color:#111;padding:14px 28px;border-radius:6px;font-weight:bold;text-decoration:none;font-size:1.2em;margin:16px}'
def page(title,body,depth,desc='',image=''):
    r='../'*depth
    og=f'<meta property="og:title" content="{html.escape(title)}"/><meta property="og:description" content="{html.escape(desc)}"/>'+(f'<meta property="og:image" content="{SITE}/{image}"/>' if image else '')
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{META()}<title>{html.escape(title)} | PlanNest Studio</title><meta name="description" content="{html.escape(desc)}">{og}<style>{CSS}</style></head><body><header><a href="{r}index.html"><img src="{r}img/logo.jpg" alt="PlanNest Studio"></a></header>{body}<footer><p><a href="https://www.etsy.com/shop/PlanNestStudioNO">Shop all on Etsy</a></p></footer></body></html>'
Image.open(f'{E}/branding/logo-black-gold_500.png').convert('RGB').save(f'{D}/docs/img/logo.jpg')
cards=[]
for x in L:
    x['img_rel']=img(f"{E}/{x['image']}",x['slug'])
    url=f"https://www.etsy.com/listing/{x['id']}"
    body=f'<main class="m"><h1>{html.escape(x["title"])}</h1><img src="../{x["img_rel"]}" alt="{html.escape(x["title"])}"><p>{html.escape(x["desc"])}</p><p><b>{x["price"]}</b></p><a class="b" href="{url}">View on Etsy &rarr;</a></main>'
    open(f"{D}/docs/p/{x['slug']}.html",'w').write(page(x['title'],body,1,x['desc'],x['img_rel']))
    cards.append(f'<div class="c"><a href="p/{x["slug"]}.html"><img src="{x["img_rel"]}" alt=""><p>{html.escape(x["title"])}</p></a></div>')
open(f'{D}/docs/index.html','w').write(page('PlanNest Studio – Event Planning Templates, Wedding Signs & Norwegian Wall Art',f'<h1>PlanNest Studio</h1><p>Event planning templates, wedding welcome signs and Norwegian wall art.</p><div class="g">{"".join(cards)}</div>',0,'Printable event planners, wedding signs and Norwegian word posters.'))
open(f'{D}/docs/.nojekyll','w').write('')
# feeds: base items (one per listing) + daily items from pins.json
pins=json.load(open(f'{D}/pins.json')) if os.path.exists(f'{D}/pins.json') else []
by={x['id']:x for x in L}
def item(title,desc,link,image,guid,date):
    return f'<item><title>{html.escape(title)}</title><link>{link}</link><guid isPermaLink="false">{guid}</guid><pubDate>{date}</pubDate><description>{html.escape(desc)}</description><enclosure url="{SITE}/{image}" type="image/jpeg" length="0"/><media:content url="{SITE}/{image}" medium="image" type="image/jpeg"/></item>'
for b,name in BOARDS.items():
    items=[]
    for p in sorted([p for p in pins if p['board']==b],key=lambda p:p['date'],reverse=True):
        x=by[p['listing_id']]; d=email.utils.format_datetime(datetime.datetime.fromisoformat(p['date']))
        items.append(item(p['title'],p['desc'],f"{SITE}/p/{x['slug']}.html?pin={p['guid']}",p['image'],p['guid'],d))
    for x in L:
        if b in x['boards'] and cfg.get('include_base_items',True):
            items.append(item(x['title'],x['desc'],f"{SITE}/p/{x['slug']}.html",x['img_rel'],f"base-{x['id']}-{b}",'Tue, 13 Oct 2026 08:00:00 +0000'))
    open(f'{D}/docs/feeds/{b}.xml','w').write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/"><channel><title>PlanNest Studio – {name}</title><link>{SITE}/</link><description>{name} by PlanNest Studio</description>{"".join(items)}</channel></rss>')
print('built',len(L),'pages,',len(pins),'pin items')
