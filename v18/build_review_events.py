import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/'v13'))
from flight_camera import FLIGHTS
from disaster_flight import ATTACKS
from outro_flight import BEATS
from semantic_score import CUES, TRANSFORMER_CUTS
from first_half_score import FIRST_HALF_CUES
events=json.loads(Path('v12/review_events.json').read_text())
for f in FLIGHTS:
    if f.name.startswith('PDOOM'):continue
    events.append(dict(t=f.time,label=f.name,kind='flight attack'))
    if f.crosses:events.append(dict(t=f.time+f.cross_age,label=f.name+' plane pass',kind='word pass'))
for t,_ in ATTACKS:events.append(dict(t=t,label='GO seismic attack',kind='earthquake'))
for t in BEATS:events.append(dict(t=t,label='continuous outro thrust',kind='drum thrust'))
for name,times in {
    'Chinese syntax machine':[26.2,26.9,27.5,29.2],
    'Smiling mask and alien body':[29.8,30.25,30.8,31.45],
    'Capability escapes training constraints':[80.85,81.5,82.1,83.2],
    'Resources become paperclips':[96.1,96.5,97.1,97.65],
    'Capability and goal are independent':[104.7,105.9,107.,108.5],
    'Data feeds dense model':[115.1,115.55,116.1,116.7],
    'Feedback mask separates':[120.3,120.9,121.7,122.25],
    'Recursive construction':[128.1,129.15,130.2,131.2],
    'Unknown remains hidden':[132.4,132.85,133.3,134.5],
}.items():
    for t in times:events.append(dict(t=t,label=name,kind='semantic action'))
unique={round(e['t'],3):e for e in events}
for name,a,b,reference,distance,scale in CUES+FIRST_HALF_CUES:
    for t,label in [(a,'semantic entrance'),(reference,'semantic subject'),(b,'semantic handoff')]:
        unique[round(t,3)]=dict(t=t,label=name,kind=label)
for t in TRANSFORMER_CUTS:unique[round(t,3)]=dict(t=t,label='Transformer computation insert',kind='camera cut')
for t,name in [(28.34,'bag onset'),(29.12,'shrooms onset'),(61.02,'basilisk onset'),(62.34,'NVDA onset'),(63.76,'moon onset'),(64.22,'Omega onset')]:unique[round(t,3)]=dict(t=t,label=name,kind='physical noun')
for t,label in [(56.2,'new containment cage'),(57.56,'FREE preload'),(57.745,'invisible blow'),(57.970,'rebound'),(58.22,'cage opening'),(62.50,'payload camera settled'),(63.26,'payload to lunar pursuit'),(63.45,'lunar camera settled'),(64.06,'moon to Omega lash'),(64.22,'Omega camera settled'),(152.5,'moving infinity entry'),(153.2,'single witness handoff'),(154.78,'loop crossover approach'),(155.15,'iris dive'),(155.8,'deep iris'),(156.6,'moving final image')]:unique[round(t,3)]=dict(t=t,label=label,kind='object choreography')
events=[unique[t] for t in sorted(unique)]
Path('v18/review_events.json').write_text(json.dumps(events,indent=2))
print(len(events),'review events')
