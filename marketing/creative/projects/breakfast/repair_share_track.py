"""Constrain the sharing display to its measured upright shape."""
from pathlib import Path
import json,math
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parent
fixed=np.float32([[199.76,672.65],[328.29,674.14],[324.87,968.38],[196.34,966.89]])
cap=cv2.VideoCapture(str(ROOT/'raw/scene-2.mp4'));fps=cap.get(cv2.CAP_PROP_FPS)
params=[];indices=[];index=0

def ordered(q):
    q=np.asarray(q,dtype=np.float32).reshape(4,2)
    s=q.sum(axis=1);d=np.diff(q,axis=1).ravel()
    return q[[np.argmin(s),np.argmin(d),np.argmax(s),np.argmax(d)]]

while True:
    ok,bgr=cap.read()
    if not ok:break
    hsv=cv2.cvtColor(bgr,cv2.COLOR_BGR2HSV)
    mask=((hsv[:,:,1]<78)&(hsv[:,:,2]>205)).astype(np.uint8)*255
    roi=np.zeros_like(mask);roi[440:1180,110:400]=mask[440:1180,110:400]
    contours,_=cv2.findContours(roi,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    candidates=[]
    for contour in contours:
        area=cv2.contourArea(contour)
        if not 8000<area<65000:continue
        q=ordered(cv2.boxPoints(cv2.minAreaRect(contour)))
        width=(np.linalg.norm(q[1]-q[0])+np.linalg.norm(q[2]-q[3]))/2
        height=(np.linalg.norm(q[3]-q[0])+np.linalg.norm(q[2]-q[1]))/2
        if not 1.65<height/max(width,1)<3.2:continue
        candidates.append((area,q))
    if candidates:
        q=max(candidates,key=lambda x:x[0])[1]
        mat,_=cv2.estimateAffinePartial2D(fixed,q,method=cv2.RANSAC,ransacReprojThreshold=8)
        if mat is not None:
            aa,bb=mat[0,0],mat[1,0]
            params.append([math.log(max(math.hypot(aa,bb),.1)),math.atan2(bb,aa),mat[0,2],mat[1,2]])
            indices.append(index)
    index+=1
cap.release()
values=np.array(params);values[:,1]=np.unwrap(values[:,1])
for col in range(4):values[:,col]=np.convolve(np.pad(values[:,col],(2,2),mode='edge'),[1/9,2/9,3/9,2/9,1/9],mode='valid')
quads={}
for i,p in zip(indices,values):
    z=math.exp(p[0]);a=p[1]
    mat=np.array([[z*math.cos(a),-z*math.sin(a),p[2]],[z*math.sin(a),z*math.cos(a),p[3]]])
    q=np.c_[fixed,np.ones(4)]@mat.T
    center=q.mean(axis=0);q=center+(q-center)*.99
    quads[str(i)]=q.tolist()
data=json.loads((ROOT/'tracking.json').read_text())
data['share']={'fps':fps,'quads':quads}
data['share_track_method']='measured upright shape + color screen similarity, five-frame smoothing'
(ROOT/'tracking.json').write_text(json.dumps(data,separators=(',',':')))
print('Corrected sharing track:',len(quads),'frames; first/last',min(indices),max(indices))
