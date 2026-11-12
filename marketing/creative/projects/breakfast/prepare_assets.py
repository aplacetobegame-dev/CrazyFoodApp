from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import requests
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
(ROOT/'raw').mkdir(parents=True,exist_ok=True);(ROOT/'build/qa').mkdir(parents=True,exist_ok=True)
status=ROOT/'generation-completed.json'
if not status.exists():status=max(ROOT.glob('generation-status-*.json'),key=lambda p:p.stat().st_mtime)
jobs=[j for j in json.loads(status.read_text())['jobs'] if j['status']=='completed']

def fetch(j):
    path=ROOT/f"raw/scene-{j['index']}.mp4"
    if not path.exists():
        r=requests.get(j['result_url'],timeout=120);r.raise_for_status();path.write_bytes(r.content)
    cap=cv2.VideoCapture(str(path));assert cap.isOpened(),path
    fps=cap.get(cv2.CAP_PROP_FPS)
    info={'index':j['index'],'job_id':j['job_id'],'width':int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
          'height':int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),'fps':fps,'frames':int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
          'size_bytes':path.stat().st_size}
    previous=None;changes=[];index=0
    while True:
        ok,bgr=cap.read()
        if not ok:break
        small=cv2.resize(bgr,(96,170))
        hist=cv2.calcHist([small],[0,1,2],None,[8,8,8],[0,256,0,256,0,256]);cv2.normalize(hist,hist)
        if previous is not None:
            score=cv2.compareHist(previous,hist,cv2.HISTCMP_BHATTACHARYYA)
            if score>.28:changes.append({'time':round(index/fps,4),'score':round(score,4)})
        previous=hist;index+=1
    info['cut_candidates']=changes
    cap.release();return info

with ThreadPoolExecutor(max_workers=4) as pool:infos=list(pool.map(fetch,jobs))
(ROOT/'build/qa/raw-metadata.json').write_text(json.dumps(infos,indent=2)+'\n')
times={0:[.5,2.4,3.7,4.9,5.6],1:[.35,1.2,2.2,3.7,5.3],2:[.3,1.1,1.9,2.7,3.6],3:[.4,1.65,2.9,4.25,4.8]}
board=Image.new('RGB',(1350,max(1,len(jobs))*520),'#FAF6EF');d=ImageDraw.Draw(board)
font=ImageFont.truetype(str(ROOT.parents[1]/'shared/brand/fonts/ibmplexmono/IBMPlexMono-Regular.ttf'),20)
for row,j in enumerate(jobs):
    cap=cv2.VideoCapture(str(ROOT/f"raw/scene-{j['index']}.mp4"))
    for column,t in enumerate(times[j['index']]):
        cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,bgr=cap.read();assert ok
        im=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB))
        im.save(ROOT/f"build/qa/raw-scene-{j['index']}-{t:.2f}.jpg",quality=95)
        board.paste(im.resize((270,480),Image.Resampling.LANCZOS),(column*270,row*520))
        d.text((column*270+8,row*520+487),f"Scene{j['index']} / {t:.2f}s",fill='#211F1C',font=font)
    cap.release()
board.save(ROOT/'build/qa/raw-review.jpg',quality=95)
print(json.dumps(infos,indent=2))
