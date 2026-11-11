from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import requests
import cv2
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
(ROOT/'raw').mkdir(exist_ok=True)
(ROOT/'qa').mkdir(exist_ok=True)
status=ROOT/'generation-completed.json'
if not status.exists():status=ROOT/'generation-status-partial.json'
jobs=[j for j in json.loads(status.read_text())['jobs'] if j['status']=='completed']

def fetch(j):
    path=ROOT/f"raw/reaction-{j['index']}.mp4"
    if not path.exists():
        r=requests.get(j['result_url'],timeout=120);r.raise_for_status();path.write_bytes(r.content)
    cap=cv2.VideoCapture(str(path))
    assert cap.isOpened(),path
    info={'index':j['index'],'job_id':j['job_id'],'width':int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
          'height':int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),'fps':cap.get(cv2.CAP_PROP_FPS),'frames':int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
          'size_bytes':path.stat().st_size}
    cap.release()
    return info

with ThreadPoolExecutor(max_workers=4) as pool:info=list(pool.map(fetch,jobs))
(ROOT/'qa/raw-reactions-metadata.json').write_text(json.dumps(info,indent=2)+'\n')
board=Image.new('RGB',(1350,len(jobs)*520),'#FAF6EF');d=ImageDraw.Draw(board)
font=ImageFont.truetype(str(ROOT.parent/'commercial-v2-plan/references/fonts/ibmplexmono/IBMPlexMono-Regular.ttf'),20)
for row,j in enumerate(jobs):
    cap=cv2.VideoCapture(str(ROOT/f"raw/reaction-{j['index']}.mp4"))
    for column,t in enumerate([.05,.8,1.6,2.4,3.6]):
        cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,bgr=cap.read();assert ok
        im=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB))
        im.save(ROOT/f"qa/actor-{j['index']}-{t:.2f}.jpg",quality=95)
        board.paste(im.resize((270,480),Image.Resampling.LANCZOS),(column*270,row*520))
        d.text((column*270+8,row*520+487),f"Actor {j['index']+1} / {t:.2f}s",fill='#211F1C',font=font)
    cap.release()
board.save(ROOT/'qa/raw-reactions-review.jpg',quality=95)
print(json.dumps(info,indent=2))
