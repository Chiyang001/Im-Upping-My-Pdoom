"""Physical noun cues and two-word coverage for the opening two verses."""
import json
from pathlib import Path

# name, start, end, camera reference, distance, scale
FIRST_HALF_CUES=(
    ('circuits',5.70,9.08,7.05,20.,1.05),
    ('control',12.99,16.20,14.95,20.,1.05),
    ('dialogue',16.20,22.19,19.8,21.,1.12),
    ('risk',22.19,24.12,23.35,19.,1.05),
    ('foom',24.12,26.06,25.5,21.,1.05),
    ('shrooms',27.8,29.68,29.2,20.,1.55),
    ('stable',38.19,41.16,40.0,20.,1.1),
    ('singularity',41.16,44.79,43.1,21.,1.1),
    ('optimization',44.79,48.645,46.45,21.,1.1),
    ('atoms',48.645,52.56,51.35,20.,1.15),
    ('sydney',52.56,58.43,56.8,20.,1.1),
    ('basilisk',60.30,62.34,61.45,17.,1.25),
    ('orbital',62.34,65.94,63.05,22.,1.30),
    ('inspection',68.20,73.87,70.5,20.,1.12),
)

def first_half_state(t):
    for name,a,b,ref,distance,scale in FIRST_HALF_CUES:
        if a<=t<b:
            return dict(active=True,name=name,start=a,end=b,u=(t-a)/(b-a),
                        reference=ref,distance=distance,scale=scale,
                        exposure=min(1.,(t-a)/.09,(b-t)/.09))
    return dict(active=False,name=None,exposure=0.)


# These are the recorded lexical groups, not a free-running tempo. A cut
# belongs to the incoming pair of sung words and never reveals future text.
_TIMELINE=json.loads(Path(__file__).with_name('word_timeline.json').read_text(encoding='utf-8'))
PHRASE_CUTS=[]
for line_index,row in enumerate(_TIMELINE):
    seen=set()
    for word in row:
        group=word['group']
        if group in seen:continue
        seen.add(group)
        if not 1.42 <= word['group_start'] < 73.87:continue
        words=[w['text'] for w in row if w['group']==group]
        PHRASE_CUTS.append(dict(start=word['group_start'],end=word['group_end'],
                                line_index=line_index,group=group,words=words))
PHRASE_CUTS=tuple(PHRASE_CUTS)

# Keep the multi-hit fracture and the precise moving-object chase intact.
# Word flights are protected dynamically by actual crossing phase in the
# camera director; their long exit corridors can receive tangential cuts.
_PROTECTED=((56.20,58.43),(62.34,65.94))

# No-word intervals still own an action: inspect the deep single-eye rim,
# then leave the doubtful inspection sample along its physical cradle.
SILENT_CUTS=(
    dict(start=35.52,end=36.70,name='iris_rim',serial=101),
    dict(start=36.70,end=38.12,name='iris_exit',serial=102),
    dict(start=72.90,end=73.33,name='approval_seam',serial=103),
    dict(start=73.33,end=73.87,name='approval_exit',serial=104),
)


def phrase_state(t):
    if any(a<=t<b for a,b in _PROTECTED):return dict(active=False)
    silent=next((c for c in SILENT_CUTS if c['start']<=t<c['end']),None)
    if silent:
        cue=dict(silent);cue.update(active=True,u=(t-cue['start'])/(cue['end']-cue['start']),
                                   words=[],line_index=-1,group=cue['serial'],silent=True)
        return cue
    cue=next((c for c in PHRASE_CUTS if c['start']<=t<c['end']),None)
    if cue is None:return dict(active=False)
    cue=dict(cue);cue['active']=True;cue['u']=(t-cue['start'])/max(.01,cue['end']-cue['start'])
    cue['serial']=PHRASE_CUTS.index(next(c for c in PHRASE_CUTS if c['start']==cue['start']))
    cue['silent']=False
    return cue
