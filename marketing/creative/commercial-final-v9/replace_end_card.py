"""Replace seconds22–25 using the regenerated end-card artwork; copy AAC audio."""
from pathlib import Path
import json
import shutil
import subprocess
import cv2
from PIL import Image

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'commercial-final-v8/food-felonies-hearts-four-reactions-25s-v8.mp4'
ART=ROOT/'end-card-generated.png'
FINAL=ROOT/'food-felonies-clean-ending-25s-v9.mp4'
FFMPEG=shutil.which('ffmpeg')
(ROOT/'qa').mkdir(exist_ok=True)

subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-i',str(ART),
                '-vf','scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1',
                '-frames:v','1',str(ROOT/'end-frame-1080x1920.png')],check=True)

filters=('[0:v]trim=end_frame=660,setpts=PTS-STARTPTS,setsar=1[main];'
         '[1:v]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,'
         'fps=30,trim=end_frame=90,setpts=PTS-STARTPTS[end];'
         '[main][end]concat=n=2:v=1:a=0,fps=30,format=yuv420p[v]')
subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-i',str(SOURCE),'-loop','1','-framerate','30','-i',str(ART),
                '-filter_complex',filters,'-map','[v]','-map','0:a:0','-c:v','libx264','-preset','fast','-crf','16',
                '-c:a','copy','-t','25','-movflags','+faststart',str(FINAL)],check=True)

probe=json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-show_streams','-show_format','-of','json',str(FINAL)],text=True))
v=next(s for s in probe['streams'] if s['codec_type']=='video')
a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert abs(float(probe['format']['duration'])-25)<.025
assert (v['width'],v['height'])==(1080,1920)
assert v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==750
decode=subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-i',str(FINAL),'-f','null','-'],capture_output=True,text=True,check=True)
assert not decode.stderr.strip(),decode.stderr

def audio_hash(path):
    return subprocess.check_output([FFMPEG,'-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip()

old_hash,new_hash=audio_hash(SOURCE),audio_hash(FINAL)
assert old_hash==new_hash,(old_hash,new_hash)
cap=cv2.VideoCapture(str(FINAL))
for t in [21.9,22,22.5,23.5,24.9]:
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000)
    ok,bgr=cap.read();assert ok,t
    Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).save(ROOT/f'qa/encoded-{t:05.2f}.jpg',quality=96)
cap.release()

report={'verified':True,'duration_seconds':25,'frames':750,'fps':30,'width':1080,'height':1920,
        'audio_codec':a['codec_name'],'audio_stream_identical_to_v8':True,'audio_sha256':new_hash,
        'decode_errors':False,'new_end_interval_seconds':[22,25],'new_end_art':'end-card-generated.png',
        'removed':['CASE CLOSED. APP OPEN.','CTA rays','old low-resolution chef','paper crop rectangles','old bottom slogan'],
        'image_generation_tool':'built-in image_gen','new_video_model_generations':0,'size_bytes':FINAL.stat().st_size}
(ROOT/'qa/final-verification.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'delivery.json').write_text(json.dumps({'video':str(FINAL),'end_frame':str(ROOT/'end-frame-1080x1920.png'),'verification':str(ROOT/'qa/final-verification.json')},indent=2)+'\n')
print(json.dumps(report,indent=2))
