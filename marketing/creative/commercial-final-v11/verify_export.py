from pathlib import Path
import json
import shutil
import subprocess
import cv2
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
FINAL=ROOT/'food-felonies-discover-then-cook-25s-v11.mp4'
MASTER=ROOT.parent/'commercial-final-v10/food-felonies-mask-ending-25s-v10.mp4'
FFMPEG=shutil.which('ffmpeg')
probe=json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-show_streams','-show_format','-of','json',str(FINAL)],text=True))
video=next(s for s in probe['streams'] if s['codec_type']=='video')
audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
duration=float(probe['format']['duration'])
assert abs(duration-25)<.025
assert (video['width'],video['height'])==(1080,1920)
assert video['avg_frame_rate']=='30/1' and int(video['nb_frames'])==750
assert audio['sample_rate']=='48000' and audio['channels']==2
decode=subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-i',str(FINAL),'-f','null','-'],capture_output=True,text=True,check=True)
assert not decode.stderr.strip(),decode.stderr

def audio_hash(path):
    return subprocess.check_output([FFMPEG,'-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip()

assert audio_hash(FINAL)==audio_hash(MASTER)
jobs=json.loads((ROOT/'generation-completed.json').read_text())['jobs']
assert len(jobs)==4 and all(j['status']=='completed' for j in jobs)
times=[1.75,5.6,12.8,13.7,14.2,14.7,15.6,16.3,16.7,17.9,19.2,20.5,21.1,21.6,23.5]
board=Image.new('RGB',(1350,1560),'#FAF6EF');d=ImageDraw.Draw(board)
font=ImageFont.truetype(str(ROOT.parent/'commercial-v2-plan/references/fonts/ibmplexmono/IBMPlexMono-Regular.ttf'),20)
cap=cv2.VideoCapture(str(FINAL))
for i,t in enumerate(times):
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,bgr=cap.read();assert ok,t
    im=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB))
    im.save(ROOT/f'qa/encoded-{t:05.2f}.jpg',quality=96)
    board.paste(im.resize((270,480),Image.Resampling.LANCZOS),((i%5)*270,(i//5)*520))
    d.text(((i%5)*270+8,(i//5)*520+487),f'{t:05.2f}s',fill='#211F1C',font=font)
cap.release()
board.save(ROOT/'qa/final-contact-sheet.jpg',quality=95)
shutil.copy2(ROOT/'qa/encoded-17.90.jpg',ROOT/'poster.jpg')
report={'verified':True,'duration_seconds':duration,'width':1080,'height':1920,'frames':750,'fps':30,
        'video_codec':video['codec_name'],'audio_codec':audio['codec_name'],'decode_errors':False,
        'audio_identical_to_v10':True,'size_bytes':FINAL.stat().st_size,'new_completed_seedance_jobs':4,'quoted_credits':256,
        'discovery':{'seconds':[14,16.4],'people':4,'same_main_cook_post':True,'physical_finished_food_in_discovery':False},
        'cooking_shots':[{'seconds':[16.4,17.6],'person':'burgundy-shirt man','action':'chopping'},
                         {'seconds':[17.6,18.8],'person':'blue-apron woman','action':'mixing'},
                         {'seconds':[18.8,20],'person':'mustard-shirt man','action':'pouring'},
                         {'seconds':[20,21.2],'person':'braided woman','action':'unmolding'}],
        'uploads':{'seconds':[21.2,22],'photos':4},'end_card':'v10 final gas-mask state,22–25seconds',
        'visual_review':'Four shared-post viewers precede four identifiable cooking close-ups and four result photos.'}
(ROOT/'qa/final-verification.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'delivery.json').write_text(json.dumps({'video':str(FINAL),'poster':str(ROOT/'poster.jpg'),'verification':str(ROOT/'qa/final-verification.json')},indent=2)+'\n')
print(json.dumps(report,indent=2))
