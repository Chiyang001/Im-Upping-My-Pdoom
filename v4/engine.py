import math,json,pathlib,subprocess,sys,random,re,difflib
import numpy as np
import moderngl as gl
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon
import mapbox_earcut as ear
import imageio_ffmpeg
W,H=1920,1080;FPS=30;DUR=156.667
C=np.array([.70,.97,.77]);WHITE=np.array([.86,.91,.94]);PURPLE=np.array([.40,.38,.95]);DARK=np.array([.09,.16,.18])
def unit(v):v=np.array(v,dtype=float);return v/max(1e-9,np.linalg.norm(v))
def tr(x=0,y=0,z=0):m=np.eye(4);m[:3,3]=[x,y,z];return m
def sc(x):return np.diag([x,x,x,1.])
def rot(a,axis=1):
 c,s=math.cos(a),math.sin(a);m=np.eye(4);i,j=[(1,2),(2,0),(0,1)][axis];m[i,i]=m[j,j]=c;m[i,j]=-s;m[j,i]=s;return m

def perspective(fov,aspect,near=.1,far=150):
 f=1/math.tan(fov/2);return np.array([[f/aspect,0,0,0],[0,f,0,0],[0,0,(far+near)/(near-far),2*far*near/(near-far)],[0,0,-1,0]])
def look(eye,target):
 f=unit(np.array(target)-eye);s=unit(np.cross(f,[0,1,0]));u=np.cross(s,f);m=np.eye(4);m[:3,:3]=[s,u,-f];m[:3,3]=-m[:3,:3]@eye;return m
class Mesh:
 def __init__(self):self.v=[];self.l=[]
 def tri(self,a,b,c,color=WHITE):
  n=unit(np.cross(np.array(b)-a,np.array(c)-a))
  for p in [a,b,c]:self.v.append([*p,*n,*color])
 def line(self,pts,color=C,closed=False):
  p=np.array(pts)
  if closed:p=np.vstack([p,p[0]])
  for a,b in zip(p[:-1],p[1:]):self.l.extend([[*a,*color],[*b,*color]])
 def add(self,other,m=None):
  m=np.eye(4) if m is None else m
  if other.v:
   a=np.array(other.v).copy();a[:,:3]=(np.c_[a[:,:3],np.ones(len(a))]@m.T)[:,:3];a[:,3:6]=a[:,3:6]@m[:3,:3].T;a[:,3:6]/=np.maximum(np.linalg.norm(a[:,3:6],axis=1)[:,None],1e-8);self.v.extend(a.tolist())
  if other.l:
   a=np.array(other.l).copy();a[:,:3]=(np.c_[a[:,:3],np.ones(len(a))]@m.T)[:,:3];self.l.extend(a.tolist())
 def circle(self,r=1,pos=(0,0,0),axis=2,color=C,n=160):
  pts=[]
  for t in np.linspace(0,math.tau,n):
   a=[r*math.cos(t),r*math.sin(t),0];a=np.roll(a,axis-2);pts.append(np.array(a)+pos)
  self.line(pts,color)
 def sphere(self,r=1,pos=(0,0,0),color=C,rings=12):
  for a in np.linspace(-1.45,1.45,rings):self.circle(r*math.cos(a),(pos[0],pos[1]+r*math.sin(a),pos[2]),1,color,100)
  for a in np.linspace(0,math.pi,rings):
   self.line([np.array(pos)+[r*math.cos(t)*math.cos(a),r*math.sin(t),r*math.cos(t)*math.sin(a)] for t in np.linspace(0,math.tau,100)],color)
 def box(self,pos,size,color=C):
  p=np.array(pos);s=np.array(size)/2;vs=[p+s*np.array([x,y,z]) for x in [-1,1] for y in [-1,1] for z in [-1,1]]
  for i,a in enumerate(vs):
   for j,b in enumerate(vs):
    if j>i and sum(a!=b)==1:self.line([a,b],color)
 def tube(self,pts,r=.04,color=C,sides=6):
  pts=np.array(pts);rings=[]
  for i,p in enumerate(pts):
   tangent=unit(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]);u=unit(np.cross(tangent,[0,1,0] if abs(tangent[1])<.9 else [1,0,0]));v=np.cross(tangent,u);rings.append([p+r*(math.cos(t)*u+math.sin(t)*v) for t in np.linspace(0,math.tau,sides,endpoint=False)])
  for a,b in zip(rings[:-1],rings[1:]):
   for j in range(sides):k=(j+1)%sides;self.tri(a[j],b[j],b[k],color);self.tri(a[j],b[k],a[k],color)
class Pen(BasePen):
 def __init__(self,gs):super().__init__(gs);self.contours=[];self.p=[]
 def _moveTo(self,p):self.p=[p]
 def _lineTo(self,p):self.p.append(p)
 def _curveToOne(self,p1,p2,p3):
  p0=self.p[-1]
  for t in np.linspace(0,1,9)[1:]:self.p.append(tuple((1-t)**3*np.array(p0)+3*(1-t)**2*t*np.array(p1)+3*(1-t)*t*t*np.array(p2)+t**3*np.array(p3)))
 def _qCurveToOne(self,p1,p2):
  p0=self.p[-1]
  for t in np.linspace(0,1,7)[1:]:self.p.append(tuple((1-t)**2*np.array(p0)+2*(1-t)*t*np.array(p1)+t*t*np.array(p2)))
 def _closePath(self):
  if len(self.p)>2:self.contours.append(self.p)
  self.p=[]
 def _endPath(self):self._closePath()
