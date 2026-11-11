"""Check and inspect the encoded v7 deliverable rather than source previews."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
FINAL=ROOT/'food-felonies-toxic-chef-25s-v7.mp4'
FFMPEG=shutil.which('ffmpeg')
probe=json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-show_streams','-show_format','-of','json',str(FINAL)],text=True))
video=next(s for s in probe['streams'] if s['codec_type']=='video')
audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
duration=float(probe['format']['duration'])
assert abs(duration-25)<.025, duration
assert (video['width'],video['height'])==(1080,1920), video
assert video['avg_frame_rate']=='30/1' and int(video['nb_frames'])==750, video
assert audio['sample_rate']=='48000' and audio['channels']==2, audio
decode=subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-i',str(FINAL),'-f','null','-'],capture_output=True,text=True,check=True)
assert not decode.stderr.strip(),decode.stderr
levels=subprocess.run([FFMPEG,'-hide_banner','-i',str(FINAL),'-af','volumedetect','-vn','-sn','-dn','-f','null','-'],capture_output=True,text=True,check=True)
peak=float(re.search(r'max_volume: ([\d.-]+)',levels.stderr).group(1))
assert peak<-.2,peak
times=[0,.35,.68,1.0,1.35,1.75,2.55,3.65,4.4,5.6,6.6,8.25,9.12,10.65,12.7,15.8,16.45,18.6,21.4,23.4]
board=Image.new('RGB',(1350,2080),'#FAF6EF')
d=ImageDraw.Draw(board)
font=ImageFont.truetype(str(ROOT.parent/'commercial-v2-plan/references/fonts/ibmplexmono/IBMPlexMono-Regular.ttf'),20)
cap=cv2.VideoCapture(str(FINAL))
for i,t in enumerate(times):
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000)
    ok,bgr=cap.read()
    assert ok,t
    frame=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB))
    frame.save(ROOT/f'qa/encoded-{t:05.2f}.jpg',quality=95)
    board.paste(frame.resize((270,480),Image.Resampling.LANCZOS),((i%5)*270,(i//5)*520))
    d.text(((i%5)*270+8,(i//5)*520+487),f'{t:05.2f}s',font=font,fill='#211F1C')
cap.release()
board.save(ROOT/'qa/final-contact-sheet.jpg',quality=95)
shutil.copy2(ROOT/'qa/encoded-04.40.jpg',ROOT/'poster.jpg')
report={'verified':True,'duration_seconds':duration,'width':1080,'height':1920,'frames':750,'fps':30,
        'video_codec':video['codec_name'],'audio_codec':audio['codec_name'],'audio_sample_rate':48000,'channels':2,
        'audio_peak_dbfs':peak,'decode_errors':False,'size_bytes':FINAL.stat().st_size,
        'new_model_video_jobs':0,'footage_model':'Seedance 2.5 (reused source clips)',
        'chef_states':6,'mascot_source':'../commercial-art-v7/chef-toxic-progression.png',
        'on_screen_ingredient_words':['ONION','GREEN PEPPER','GELATIN','CELERY'],
        'native_voice_tracks_included':False,'quiet_kitchen_audio_global_seconds':[6,9.12],
        'soundtrack':'../commercial-final-v6/audio/guitar-drums-original.mp3'}
(ROOT/'qa/final-verification.json').write_text(json.dumps(report,indent=2)+'\n')
delivery={'video':str(FINAL),'poster':str(ROOT/'poster.jpg'),'verification':str(ROOT/'qa/final-verification.json'),'duration_seconds':25}
(ROOT/'delivery.json').write_text(json.dumps(delivery,indent=2)+'\n')
print(json.dumps(report,indent=2))
