"""Finite, word-motivated scenes; instrumental gaps continue an action."""

# name, start, end, fixed camera reference, distance, scale
CUES=(
 ('sparks',0.,5.58,3.7,20.,1.12),
 ('circuits',5.58,9.08,7.1,20.,1.12),
 ('loss',9.08,12.99,10.2,20.,1.13),
 ('hierarchy',12.99,16.2,14.5,21.,1.15),
 ('risk1',22.19,25.685,23.3,23.,1.65),
 ('shinigami',31.83,38.19,34.9,20.,1.13),
 ('stable',38.19,41.16,39.8,20.,1.15),
 ('optimizing',44.79,48.645,46.4,20.,1.15),
 ('sydney',52.56,58.43,55.7,19.,1.18),
 ('basilisk',60.86,62.34,61.5,20.,1.1),
 ('moon',62.34,64.22,63.2,16.,1.3),
 ('omega',64.22,65.94,65.,14.,1.35),
 ('compute',65.94,68.185,67.,20.,1.2),
 ('approval',68.185,73.87,70.9,19.,1.17),
 ('mlp',73.87,77.24,75.1,20.,1.16),
 ('vonneumann',77.24,80.68,78.9,20.,1.15),
 ('cdr',84.78,89.995,87.1,20.,1.12),
 ('gato',89.995,94.06,92.,20.,1.16),
 ('killswitch',98.845,102.32,100.5,19.,1.15),
 ('fuse',102.32,104.33,103.35,18.,1.18),
 ('transformer',109.33,115.,111.6,24.,1.4),
 ('gpu',118.645,120.18,119.4,20.,1.2),
 ('branch_seed',122.54,124.04,123.3,20.,1.25),
 ('loom',125.86,127.96,127.2,20.,1.25),
 ('masked',127.96,129.60,128.8,22.,1.2),
 ('unknown',132.22,136.83,134.6,18.,1.45),
 ('show',136.83,141.2,138.7,21.,1.3),
)

def semantic_state(t):
 for name,a,b,ref,distance,scale in CUES:
  if a<=t<b:
   return dict(active=True,name=name,start=a,end=b,u=(t-a)/(b-a),
               reference=ref,distance=distance,scale=scale,
               exposure=min(1.,(t-a)/.075,(b-t)/.075))
 return dict(active=False,name=None,exposure=0.)

TRANSFORMER_CUTS=(109.82,110.40,111.15,112.42,113.26,114.10)

def transformer_insert(t):
 """Several real camera inserts around the same fixed world apparatus."""
 keys=((109.82,110.40,(-2.,1.,0.),(1.,0.,-1.),-.03),
       (110.40,111.15,(4.,1.,.8),(1.,-1.,-.8),.075),
       (111.15,112.42,(-5.,2.,.5),(-1.,-1.,-1.),-.08),
       (112.42,113.26,(1.,-4.,.2),(-1.,-1.,-1.),.05),
       (113.26,114.10,(3.,3.,.4),(-1.,1.,-.5),-.04))
 for a,b,p,q,roll in keys:
  if a<=t<b:
   u=(t-a)/(b-a)
   return dict(offset=[p[j]+q[j]*u for j in range(3)],roll=roll,u=u)
 return None
