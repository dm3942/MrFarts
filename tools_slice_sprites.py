"""Slice the sprite-sheet JPGs into transparent PNGs (sprites/ folder).
Background removal = flood fill of near-white pixels reachable from the crop border,
so white gloves / eyes inside the outlines are kept."""
from PIL import Image
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sprites")
os.makedirs(OUT, exist_ok=True)

SHEETS = {
    "MrFarts.jpg": {
        "mf_idle":      (290,125,400,320),
        "mf_run1":      (490,125,620,320),
        "mf_run2":      (650,125,800,320),
        "mf_run3":      (820,125,975,320),
        "mf_run4":      (990,125,1140,320),
        "mf_jump":      (55,380,215,525),
        "mf_boost":     (310,375,520,535),
        "mf_fall":      (630,380,810,500),
        "mf_land":      (870,375,1030,540),
        "mf_crouch":    (95,590,250,760),
        "mf_celebrate": (720,580,900,770),
        "fart_cloud":   (895,585,990,650),
        "boost_cloud":  (300,520,520,650),
    },
    "Grandma.jpg": {
        "gm_idle":   (35,65,300,360),
        "gm_walk1":  (405,65,610,360),
        "gm_walk2":  (660,65,870,360),
        "gm_walk3":  (905,65,1110,360),
        "gm_swing1": (15,455,200,715),
        "gm_swing2": (255,455,540,715),
        "gm_shock":  (560,455,700,715),
        "gm_point":  (900,455,1110,735),
    },
    "Police.jpg": {
        "po_idle":    (30,125,215,375),
        "po_run":     (245,125,470,375),
        "po_swing":   (480,125,735,375),
        "po_caught":  (740,160,905,375),
        "po_whistle": (950,125,1150,375),
        "po_run2":    (245,440,470,690),
    },
    "Kids.jpg": {
        "kid_boy_run":    (30,185,170,380),
        "kid_girl1_run":  (185,185,345,380),
        "kid_girl2_run":  (360,185,500,380),
        "kid_boy_look":   (640,470,760,660),
        "kid_girl1_look": (780,470,920,660),
        "kid_girl2_look": (950,470,1090,660),
        "kid_boy_point":  (640,185,760,380),
        "kid_girl1_point":(775,185,940,380),
        "kid_girl2_point":(950,185,1120,380),
    },
}

def is_bg(p, thr):
    r, g, b = p[:3]
    return r > thr and g > thr and b > thr and (max(r,g,b) - min(r,g,b)) < 40

def key_out(im, thr=185):
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    seen = bytearray(w*h)
    stack = []
    for x in range(w):
        stack.append((x,0)); stack.append((x,h-1))
    for y in range(h):
        stack.append((0,y)); stack.append((w-1,y))
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= w or y >= h: continue
        i = y*w+x
        if seen[i]: continue
        seen[i] = 1
        if not is_bg(px[x,y], thr): continue
        px[x,y] = (255,255,255,0)
        stack.append((x+1,y)); stack.append((x-1,y)); stack.append((x,y+1)); stack.append((x,y-1))
    # soften edge: semi-transparent light pixels bordering the removed region
    for y in range(h):
        for x in range(w):
            r,g,b,a = px[x,y]
            if a == 0: continue
            if min(r,g,b) > 150:
                nb = 0
                for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    xx,yy = x+dx,y+dy
                    if 0<=xx<w and 0<=yy<h and px[xx,yy][3]==0: nb += 1
                if nb:
                    k = min(r,g,b)
                    alpha = int(max(0, min(255, (255-k)*2.2)))
                    px[x,y] = (r,g,b,alpha)
    return im

for sheet, crops in SHEETS.items():
    src = Image.open(os.path.join(HERE, sheet))
    for name, box in crops.items():
        im = key_out(src.crop(box))
        bbox = im.getbbox()
        if bbox: im = im.crop(bbox)
        im.save(os.path.join(OUT, name + ".png"))
        print(f"{name:18s} {im.size}")
