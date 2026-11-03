import sys,os,base64,hashlib
from PIL import Image
slug=sys.argv[1]; src=f'img/{slug}-src.webp' if os.path.exists(f'img/{slug}-src.webp') else f'img/{slug}.webp'
im=Image.open(src).convert('RGB'); best=None
for w in (800,720,640):
    for q in (50,42,35,28):
        r=im.resize((w,round(im.height*w/im.width)),Image.LANCZOS); p=f'/tmp/{slug}-up.webp'
        r.save(p,'WEBP',quality=q,method=6); n=len(base64.b64encode(open(p,'rb').read()))
        if n<=22000: best=(w,q,n); break
    if best: break
r.save(f'/tmp/{slug}-prev.jpg',quality=70)
print(slug,'width',r.size[0],'q',best[1] if best else q,'b64',n,'md5',hashlib.md5(open(p,'rb').read()).hexdigest())
