import json
from pathlib import Path
from flight_camera import FLIGHTS
from disaster_flight import ATTACKS
from outro_flight import BEATS
events=json.loads(Path('v12/review_events.json').read_text())
for f in FLIGHTS:
    if f.name.startswith('PDOOM'):continue
    events.append(dict(t=f.time,label=f.name,kind='flight attack'))
    if f.crosses:events.append(dict(t=f.time+f.cross_age,label=f.name+' plane pass',kind='word pass'))
for t,_ in ATTACKS:events.append(dict(t=t,label='GO seismic attack',kind='earthquake'))
for t in BEATS:events.append(dict(t=t,label='continuous outro thrust',kind='drum thrust'))
unique={round(e['t'],3):e for e in events}
events=[unique[t] for t in sorted(unique)]
Path('v13/review_events.json').write_text(json.dumps(events,indent=2))
print(len(events),'review events')
