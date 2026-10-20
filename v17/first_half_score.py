"""Additional physical nouns. Later scenes and original eye shots are retained."""

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
