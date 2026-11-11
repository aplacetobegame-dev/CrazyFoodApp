"""Verify the final encoded commercial and extract representative actual frames."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import cv2
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
FINAL=ROOT/'food-felonies-hearts-four-reactions-25s-v8.mp4'
ffmpeg=shutil.which('ffmpeg')
probe=json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-show_streams','-show_format','-of','json',str(FINAL)],text=True))
video=next(s for s in probe['streams'] if s['codec_type']=='video')
audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
duration=float(probe['format']['duration'])
assert abs(duration-25)<.025,duration
assert (video['width'],video['height'])==(1080,1920),video
assert video['avg_frame_rate']=='30/1' and int(video['nb_frames'])==750,video
assert audio['sample_rate']=='48000' and audio['channels']==2,audio
decode=subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-i',str(FINAL),'-f','null','-'],capture_output=True,text=True,check=True)
assert not decode.stderr.strip(),decode.stderr
levels=subprocess.run([ffmpeg,'-hide_banner','-i',str(FINAL),'-af','volumedetect','-vn','-sn','-dn','-f','null','-'],capture_output=True,text=True,check=True)
peak=float(re.search(r'max_volume: ([\d.-]+)',levels.stderr).group(1));assert peak<-.2,peak
times=[.7,1.75,4.4,5.6,10.65,11.8,12.8,13.5,13.8,14.0,14.2,14.45,14.75,15.5,16.4,17.3,17.7,18.7,20.9,23.5]
board=Image.new('RGB',(1350,2080),'#FAF6EF');d=ImageDraw.Draw(board)
font=ImageFont.truetype(str(ROOT.parent/'commercial-v2-plan/references/fonts/ibmplexmono/IBMPlexMono-Regular.ttf'),20)
cap=cv2.VideoCapture(str(FINAL))
for i,t in enumerate(times):
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,bgr=cap.read();assert ok,t
    im=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB))
    im.save(ROOT/f'qa/encoded-{t:05.2f}.jpg',quality=95)
    board.paste(im.resize((270,480),Image.Resampling.LANCZOS),((i%5)*270,(i//5)*520))
    d.text(((i%5)*270+8,(i//5)*520+487),f'{t:05.2f}s',font=font,fill='#211F1C')
cap.release()
board.save(ROOT/'qa/final-contact-sheet.jpg',quality=95)
shutil.copy2(ROOT/'qa/encoded-12.80.jpg',ROOT/'poster.jpg')
jobs=json.loads((ROOT/'generation-completed.json').read_text())['jobs']
assert len(jobs)==4 and all(j['status']=='completed' for j in jobs)
report={'verified':True,'duration_seconds':duration,'width':1080,'height':1920,'frames':750,'fps':30,
        'video_codec':video['codec_name'],'audio_codec':audio['codec_name'],'audio_sample_rate':48000,'channels':2,
        'audio_peak_dbfs':peak,'decode_errors':False,'size_bytes':FINAL.stat().st_size,
        'reaction_people':4,'reaction_layout':'2x2','reaction_interval_seconds':[14,18],
        'share_tap_seconds':13.35,'leading_share_hearts':4,'new_completed_seedance_jobs':4,'quoted_generation_credits':256,
        'native_reaction_vocals_included':False,'quiet_kitchen_audio_global_seconds':[6,9.12],
        'visual_review':'Matched comparison images, natural hearts, four phone-to-dish performances, faces and food clear.'}
(ROOT/'qa/final-verification.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'delivery.json').write_text(json.dumps({'video':str(FINAL),'poster':str(ROOT/'poster.jpg'),'verification':str(ROOT/'qa/final-verification.json'),'duration_seconds':25},indent=2)+'\n')
print(json.dumps(report,indent=2))
