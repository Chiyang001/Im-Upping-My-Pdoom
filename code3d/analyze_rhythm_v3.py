"""Deterministic, offline rhythm features for the procedural MV.

Uses scipy/numpy only. Run from any directory:
    python code3d/analyze_rhythm_v3.py

The mix is not a multitrack recording: kick/snare/hat labels are frequency-
based transient classifications, not source-separated drum stems. `events`
contains measured transients; `beats` contains a stable inferred metric grid.
Never drive a kick flash from `beats` without also considering its strength.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import ndimage, signal
from scipy.io import wavfile


ROOT = Path(__file__).resolve().parents[1]
HOP = 80
NFFT = 512


def robust_scale(a, q=97):
    return a / max(float(np.percentile(a, q)), 1e-10)


def peak_events(curve, times, kind, min_gap, height, prominence):
    dt = times[1] - times[0]
    p, _ = signal.find_peaks(curve, distance=round(min_gap/dt),
                             height=height, prominence=prominence)
    p = p[times[p] < times[-1] - .20]
    return [{"t": round(float(times[i]), 4),
             "strength": round(float(np.clip(curve[i], .0, 1.5)/1.5), 4),
             "type": kind} for i in p]


def main():
    sr, x = wavfile.read(ROOT / 'work/audio.wav')
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float32)
    x /= max(float(np.max(np.abs(x))), 1e-9)
    duration = len(x)/sr
    f, ts, z = signal.stft(x, fs=sr, nperseg=NFFT,
                            noverlap=NFFT-HOP, boundary='zeros')
    mag = np.abs(z)
    # Compression makes quieter sections measurable without a global peak gate.
    comp = np.log1p(mag * 200)
    flux = np.maximum(0, np.diff(comp, axis=1, prepend=comp[:, :1]))
    dt = HOP/sr

    def band(lo, hi):
        a = flux[(f >= lo) & (f < hi)].mean(axis=0)
        a = ndimage.gaussian_filter1d(a, .007/dt)
        # Subtract the local floor to suppress vowels and sustained synthesizers.
        floor = ndimage.median_filter(a, size=int(.70/dt)//2*2+1)
        a = np.maximum(0, a - .50*floor)
        return robust_scale(a)

    low = band(31, 187)
    mid = band(187, 3187)
    high = band(3187, 7900)
    full = robust_scale(.45*low + .35*mid + .20*high)
    # Low transients coincident with broad attacks remain kicks. Snare emphasizes
    # mid/high attacks and rejects isolated bass changes or speech consonants.
    kick = robust_scale(low * (.65+.35*np.minimum(mid, 1.0)))
    snare = robust_scale(np.sqrt(np.maximum(mid*high, 0)))
    hat = robust_scale(high / (1+.35*low))

    # Tempo from autocorrelation, then a fine grid search around the strongest
    # musical candidate. Search the dance-tempo octave (100--160) explicitly.
    stable = full[(ts > 22) & (ts < 88)]
    ac = signal.fftconvolve(stable, stable[::-1], mode='full')[len(stable)-1:]
    lag_min, lag_max = round(60/160/dt), round(60/100/dt)
    best_lag = lag_min + np.argmax(ac[lag_min:lag_max+1])
    initial_bpm = 60/(best_lag*dt)
    # Integrate a compact onset kernel at predicted beat instants. A nearest-
    # sample approach is excessively sensitive to drum attack width.
    grid_curve = ndimage.gaussian_filter1d(full, .014/dt)
    best = (-np.inf, 0., 0.)
    for bpm in np.linspace(initial_bpm-2.5, initial_bpm+2.5, 1001):
        period = 60/bpm
        for phase in np.arange(0, period, .005):
            tt = np.arange(phase, duration-.3, period)
            use = tt[(tt > 22) & (tt < 88)]
            score = np.mean(np.interp(use, ts, grid_curve))
            if score > best[0]:
                best = (float(score), float(bpm), float(phase))
    _, bpm, phase = best
    period = 60/bpm
    # Refine with all full-drum portions, excluding the deliberate bridge break.
    best_all = (-np.inf, bpm, phase)
    for b in np.linspace(bpm-.12, bpm+.12, 97):
        p = 60/b
        for ph in np.arange(max(0, phase-.03), min(p, phase+.03), .001):
            tt = np.arange(ph, duration-.3, p)
            use = tt[((tt > 22) & (tt < 88)) | ((tt > 111) & (tt < 151))]
            score = np.mean(np.interp(use, ts, grid_curve))
            if score > best_all[0]:
                best_all = (float(score), float(b), float(ph))
    _, bpm, phase = best_all
    period = 60/bpm

    kicks = peak_events(kick, ts, 'kick', .17, .35, .22)
    snares = peak_events(snare, ts, 'snare', .17, .40, .27)
    hats = peak_events(hat, ts, 'hat', .095, .45, .30)
    ons = peak_events(full, ts, 'onset', .095, .33, .23)
    # Avoid counting hats/onsets as extra flashes on the same drum attack.
    # Kicks and snares can coexist and retain both frequency-specific signals.
    rhythm_times = np.array([a['t'] for a in kicks+snares])
    hats = [a for a in hats if np.min(np.abs(rhythm_times-a['t'])) > .045]
    known_times = np.array([a['t'] for a in kicks+snares+hats])
    ons = [a for a in ons if np.min(np.abs(known_times-a['t'])) > .050]
    raw_events = sorted(kicks+snares+hats+ons, key=lambda a: a['t'])
    # One visible impulse per actual attack. A kick often excites the entire
    # spectrum, so separate band detectors must not create two camera jolts.
    groups = []
    for event in raw_events:
        if groups and event['t']-groups[-1][0]['t'] < .055:
            groups[-1].append(event)
        else:
            groups.append([event])
    events = []
    for group in groups:
        strongest = max(group, key=lambda a:a['strength'])
        components = {a['type']:a['strength'] for a in group}
        events.append({**strongest, 'components':components})

    beat_times = np.arange(phase, duration-.25, period)
    # Select bar phase using consistent four-on-floor bass accents, plus the
    # four chorus entries (which have vocal pickups before the main downbeat).
    chorus_starts = np.array([22.2, 58.4, 94.86, 124.04])
    phase_scores = []
    for offset in range(4):
        bt = beat_times[offset::4]
        strong = bt[(bt > 20) & (bt < 151)]
        drum_score = np.mean(np.interp(strong, ts, .7*kick+.3*full))
        entry_score = np.mean(np.exp(-np.min(np.abs(bt[:, None]-chorus_starts), axis=0)**2/.40))
        phase_scores.append(float(drum_score+.6*entry_score))
    downbeat_offset = int(np.argmax(phase_scores))
    beats = []
    for i, t in enumerate(beat_times):
        mask = np.abs(ts-t) < .045
        measured = max(float(np.max(full[mask])), .0)
        strength = float(np.clip(measured/1.5, 0, 1))
        beats.append({"t": round(float(t), 4), "strength": round(strength, 4),
                      "type": "downbeat" if (i-downbeat_offset)%4 == 0 else "beat",
                      "beat": int((i-downbeat_offset)%4),
                      "observed": bool(measured > .32)})

    # Primary hits: measured attacks close to musical beats plus conspicuous
    # syncopations. These are the recommended renderer camera/geometry impulses.
    impacts = []
    for e in events:
        distance = float(np.min(np.abs(beat_times-e['t'])))
        # Weak between-beat articulation drives only small line detail. Clear
        # eighth-note fills can punch through if their attack is strong enough.
        accepted = (distance < .065 and e['strength'] >= .28) or e['strength'] >= .78
        if accepted:
            impacts.append({"t":e['t'], "strength":e['strength'], "type":e['type'],
                            "on_beat":distance < .065})

    lyrics = json.loads((ROOT / 'work/lyrics.json').read_text(encoding='utf-8-sig'))
    sections = [(0, 'intro'), (1.42, 'verse_1'), (16.2, 'pre_1'),
                (22.2, 'chorus_1'), (36.5, 'turnaround_1'), (38.12, 'verse_2'),
                (52.56, 'pre_2'), (58.4, 'chorus_2'), (72.9, 'turnaround_2'),
                (73.96, 'bridge_1'), (89.86, 'pre_3'), (94.86, 'chorus_3'),
                (109.4, 'bridge_2'), (124.04, 'chorus_4'), (141.2, 'outro')]
    section_data = []
    for i, (start, name) in enumerate(sections):
        end = sections[i+1][0] if i+1 < len(sections) else duration
        ev = [a for a in events if start <= a['t'] < end]
        section_data.append({"name": name, "start": start, "end": round(end,4),
                             "bpm": round(bpm,4), "event_count": len(ev),
                             "intensity": round(float(np.mean(full[(ts >= start)&(ts < end)])),4)})

    # Scene changes follow the vocal boundary while the major impact is snapped
    # to an observed transient nearby. Keeping both is useful for anticipations.
    transitions = []
    for i, row in enumerate(lyrics):
        start, end, _, text, focus = row
        nearby = [a for a in kicks+snares+ons if abs(a['t']-start) < .26]
        selected = max(nearby, key=lambda a: a['strength']*np.exp(-abs(a['t']-start)/.18)) if nearby else None
        t = selected['t'] if selected else float(beat_times[np.argmin(np.abs(beat_times-start))])
        transitions.append({"t": t, "lyric_start": start, "lyric_end": end,
                            "lyric_index": i, "focus": focus,
                            "strength": max(.5, selected['strength']) if selected else .5,
                            "type": "chorus_cut" if i in [5,14,23,30] else "lyric_cut",
                            "text": text.replace('|',' ')})
    # A curated set of clear section accents, plus one accent for each bar.
    bar_accents = []
    for beat in beats:
        if beat['type'] != 'downbeat':
            continue
        close = [a for a in kicks+snares if abs(a['t']-beat['t']) < .08]
        if close:
            hit = max(close, key=lambda a:a['strength'])
            if hit['strength'] >= .30:
                bar_accents.append({"t":hit['t'], "strength":hit['strength'], "type":"bar_accent"})

    old = np.array(json.loads((ROOT/'work/beats.json').read_text()))
    gaps = [(round(float(a),3),round(float(b),3),round(float(b-a),3))
            for a,b in zip(old[:-1],old[1:]) if b-a > period*1.60]
    missing = [a for a in events if 89 <= a['t'] <= 110 and np.min(abs(old-a['t'])) > .09]
    old_report = {"old_count":len(old), "long_gaps":gaps,
                  "measured_events_missing_89_to_110":len(missing),
                  "largest_gap_seconds":round(float(np.max(np.diff(old))),3),
                  "issue":"Global amplitude peak gate misses many low-frequency attacks and bridge transients. The old array also mixes irregular onsets with metric beats."}

    # Low-rate continuous envelopes give smooth low-cost camera/geometry motion.
    envelope_times = np.arange(0, duration, 1/60)
    envelopes = {"fps":60, "start":0,
                 **{name:np.round(np.clip(np.interp(envelope_times, ts, curve),0,1.5)/1.5,4).tolist()
                    for name,curve in [('kick',kick),('snare',snare),('high',hat),('full',full)]}}
    result = {"version":3, "duration":round(duration,6), "sample_rate":sr,
              "bpm":round(bpm,6), "beat_period":round(period,7),
              "beat_phase":round(phase,6), "downbeat_offset":downbeat_offset,
              "timing_resolution_seconds":dt,
              "notes":["events are measured attacks; beats are inferred metric grid",
                       "mix-band classification is approximate; kick and snare may coincide",
                       "lyrics use the existing hand-corrected timeline",
                       "use narrow attack (10--30 ms) and 90--160 ms decay for kick camera impulses",
                       "bridge has real attacks absent from old beats.json; preserve its lower average energy"],
              "events":events, "impacts":impacts, "beats":beats, "transitions":transitions,
              "bar_accents":bar_accents, "sections":section_data,
              "envelopes":envelopes, "previous_beats_audit":old_report}
    output = ROOT/'code3d/rhythm_v3.json'
    output.write_text(json.dumps(result, ensure_ascii=False, separators=(',',':')),encoding='utf-8')
    print(json.dumps({"output":str(output), "bpm":bpm, "phase":phase,
                      "period":period,"events":len(events),
                      "counts":{k:sum(a['type']==k for a in events) for k in ['kick','snare','hat','onset']},
                      "beats":len(beats), "impacts":len(impacts), "bar_accents":len(bar_accents),
                      "old_audit":old_report},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
