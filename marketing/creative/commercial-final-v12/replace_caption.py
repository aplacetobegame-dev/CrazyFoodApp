"""Replace the grin-shot captions with one correctly typeset question."""
from pathlib import Path
import importlib.util
import json
import shutil
import subprocess
import cv2
from PIL import Image,ImageEnhance

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v7',ROOT.parent/'commercial-final-v7/render_commercial.py')
v7=importlib.util.module_from_spec(spec);spec.loader.exec_module(v7)
v5=v7.v5
SOURCE=ROOT.parent/'commercial-final-v11/food-felonies-discover-then-cook-25s-v11.mp4'
FINAL=ROOT/'food-felonies-dare-to-cook-25s-v12.mp4'
FFMPEG=shutil.which('ffmpeg')
(ROOT/'qa').mkdir(exist_ok=True)

def frame(t,reader):
    im=Image.fromarray(reader.get(t))
    im=ImageEnhance.Contrast(im).enhance(1.035)
    im=ImageEnhance.Color(im).enhance(1.055)
    im=v7.previous.punch(im,t).convert('RGBA')
    layer=v5.new_layer()
    v7.floating(layer,'Do I dare to cook this?',(360,1070),54,t-3.21,v7.PAPER,-4,life=1.59,drift=1.2)
    return Image.alpha_composite(im,layer).convert('RGB')

segment=ROOT/'caption-segment.mp4'
cmd=[FFMPEG,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30',
     '-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p',str(segment)]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
reader=v5.Reader(v7.SOURCE/'raw/scene-0.mp4')
for i in range(95,144):proc.stdin.write(frame(i/30,reader).tobytes())
proc.stdin.close();reader.cap.release()
if proc.wait():raise RuntimeError('Caption segment render failed')

filters=('[0:v]trim=end_frame=95,setpts=PTS-STARTPTS[a];'
         '[1:v]setpts=PTS-STARTPTS[b];'
         '[0:v]trim=start_frame=144:end_frame=750,setpts=PTS-STARTPTS[c];'
         '[a][b][c]concat=n=3:v=1:a=0,fps=30,format=yuv420p[v]')
subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-i',str(SOURCE),'-i',str(segment),
                '-filter_complex',filters,'-map','[v]','-map','0:a:0','-c:v','libx264','-preset','fast','-crf','16',
                '-c:a','copy','-t','25','-movflags','+faststart',str(FINAL)],check=True)

probe=json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-show_streams','-show_format','-of','json',str(FINAL)],text=True))
video=next(s for s in probe['streams'] if s['codec_type']=='video')
assert abs(float(probe['format']['duration'])-25)<.025
assert (video['width'],video['height'])==(1080,1920)
assert int(video['nb_frames'])==750 and video['avg_frame_rate']=='30/1'
decode=subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-i',str(FINAL),'-f','null','-'],capture_output=True,text=True,check=True)
assert not decode.stderr.strip(),decode.stderr

def audio_hash(path):
    return subprocess.check_output([FFMPEG,'-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip()

assert audio_hash(SOURCE)==audio_hash(FINAL)
cap=cv2.VideoCapture(str(FINAL))
for t in [3.4,3.8,4.4,4.7]:
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,bgr=cap.read();assert ok
    Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).save(ROOT/f'qa/encoded-{t:.2f}.jpg',quality=96)
cap.release()
report={'verified':True,'duration_seconds':25,'width':1080,'height':1920,'frames':750,'fps':30,
        'caption':'Do I dare to cook this?','replaced_grin_captions':['BAD IDEA?','PERFECT.'],
        'replaced_video_frames':[95,144],'audio_identical_to_v11':True,'decode_errors':False,'new_generation_jobs':0}
(ROOT/'qa/final-verification.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'delivery.json').write_text(json.dumps({'video':str(FINAL),'verification':str(ROOT/'qa/final-verification.json')},indent=2)+'\n')
print(json.dumps(report,indent=2))
