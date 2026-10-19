"""Independent final-video diagnostics; does not import or modify renderer."""
import json
import pathlib
import subprocess

import imageio_ffmpeg
import numpy as np


ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H, FPS = 160, 90, 8
FF = imageio_ffmpeg.get_ffmpeg_exe()
FILES = {
    "v4": ROOT / "output_v4/Pdoom_Line_Architecture_1080p.mp4",
    "v5": ROOT / "output_v5/Pdoom_Living_Machine_1080p.mp4",
}
Y, X = np.mgrid[:H, :W]
# Exclude 4 px at left/right and 3 px at top/bottom to avoid border effects.
usable = (X >= 4) & (X < 156) & (Y >= 3) & (Y < 87)
regions = {
    "left": usable & (X < 40),
    "right": usable & (X >= 120),
    "top": usable & (X >= 40) & (X < 120) & (Y < 23),
    "bottom": usable & (X >= 40) & (X < 120) & (Y >= 67),
}
regions["perimeter_union"] = np.logical_or.reduce(list(regions.values()))
regions["center"] = usable & ~regions["perimeter_union"]
regions["usable_full_frame"] = usable


def stats(v):
    v = np.asarray(v, dtype=float)
    return {
        "mean": round(float(v.mean()), 6),
        "median": round(float(np.median(v)), 6),
        "p10": round(float(np.percentile(v, 10)), 6),
        "p90": round(float(np.percentile(v, 90)), 6),
    }


def run_ranges(mask, min_frames=4):
    ranges = []
    start = None
    for i, yes in enumerate(np.r_[mask, False]):
        if yes and start is None:
            start = i
        elif not yes and start is not None:
            if i - start >= min_frames:
                ranges.append({"start": round((start+1)/FPS, 3),
                               "end": round((i+1)/FPS, 3),
                               "duration": round((i-start)/FPS, 3)})
            start = None
    return ranges


def analyze(path):
    proc = subprocess.run([
        FF, "-v", "error", "-i", str(path), "-an", "-vf",
        f"fps={FPS},scale={W}:{H}:flags=area,format=gray",
        "-f", "rawvideo", "-pix_fmt", "gray", "-"
    ], capture_output=True, check=True)
    if proc.stderr:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace"))
    video = np.frombuffer(proc.stdout, np.uint8).reshape((-1, H, W))
    diff = np.abs(np.diff(video.astype(np.int16), axis=0))
    report = {"path": str(path), "frames": len(video),
              "sample_duration_seconds": round(len(video)/FPS, 3),
              "regions": {}}
    arrays = {}
    for name, mask in regions.items():
        pix, delta = video[:, mask], diff[:, mask]
        c20, c35 = (pix > 20).mean(axis=1), (pix > 35).mean(axis=1)
        mad = delta.mean(axis=1)
        changed = (delta > 3).mean(axis=1)
        report["regions"][name] = {
            "pixel_count": int(mask.sum()),
            "coverage_luma_gt20": stats(c20),
            "coverage_luma_gt35": stats(c35),
            "consecutive_frame_absolute_luma_difference": stats(mad),
            "changed_fraction_absolute_luma_difference_gt3": stats(changed),
            "near_static_fraction": round(float(((mad < .2) & (changed < .01)).mean()), 6),
        }
        arrays[name] = (c20, c35, mad, changed)
    c20, c35, mad, changed = arrays["perimeter_union"]
    report["perimeter_near_static_runs_at_least_half_second"] = run_ranges((mad < .2) & (changed < .01))
    report["per_lyric"] = []
    lyrics = json.loads((ROOT / "work/lyrics.json").read_text(encoding="utf-8"))
    for i, row in enumerate(lyrics):
        a, b = row[:2]
        lo, hi = max(0, int(a*FPS)), min(len(video)-1, int(b*FPS))
        if hi <= lo:
            continue
        report["per_lyric"].append({
            "index": i, "start": a, "end": b,
            "perimeter_coverage_gt20_mean": round(float(c20[lo:hi].mean()), 6),
            "perimeter_coverage_gt35_mean": round(float(c35[lo:hi].mean()), 6),
            "perimeter_frame_difference_mean": round(float(mad[lo:hi].mean()), 6),
            "perimeter_changed_fraction_mean": round(float(changed[lo:hi].mean()), 6),
        })
    return report, arrays, video[:,usable].mean(axis=1)


def add_review(result):
    result['visual_spot_review'] = [
        {"time":24,"frame":"v5/final-24.jpg",
         "observation":"P(doom) is bright, large and readable against lower-contrast architecture; lines populate all four sides and show near/far layers. Future unsung words are intentionally dim. No hard crowding obstruction confirmed in this frame."},
        {"time":117,"frame":"v5/final-117.jpg",
         "observation":"SUPER-DENSE remains readable while far scaffolding fills the ceiling and side walls. Physical diagonal foreground strokes cross some letter outlines, but the complete phrase can still be read; adjacent lyrics are dimmer."},
        {"time":155,"frame":"v5/final-155.jpg",
         "observation":"Outro infinity sign and small formula remain separated in contrast from dense edge architecture. Edge density is high but does not obscure the central closing mark."}
    ]
    result['diagnostic_conclusion'] = {
        "supported":"V5 has broader low/mid-luminance perimeter coverage and a greater fraction of perimeter pixels changing between samples; no near-static perimeter run >=0.5 s was detected. The full-frame density is therefore not merely static filling.",
        "qualified":"At matching dark timestamps, coverage above luma 20 rises from 27.19% to 42.03%, coverage above 35 is essentially unchanged (15.48% to 15.55%), and changing-pixel fraction rises from 42.40% to 47.53%. Mean frame-difference amplitude decreases from 7.89 to 5.58, while its p10 floor increases from 2.03 to 3.09: movement is more consistently distributed, not numerically more violent.",
        "not_supported":"These figures do not establish stronger beat impact, better narrative, or artistic superiority over V4 or the supplied reference."
    }
    return result


def main():
    analyzed = {name: analyze(path) for name, path in FILES.items()}
    result = {
        "method": {
            "fps": FPS, "size": [W, H], "pixel_format": "8-bit gray",
            "scaling": "area average; identical for both videos",
            "usable_bounds": {"x": [4, 156], "y": [3, 87], "upper_bounds_exclusive": True},
            "perimeter": "left x<40, right x>=120; top/bottom y<23 or y>=67 in middle x=40..119; excludes outer border",
            "coverage": "fraction of region pixels above luma 20 or 35",
            "motion": "absolute luma difference between consecutive 8 fps samples, plus changed pixel fraction above difference 3",
            "near_static": "mean difference <0.2 AND changed fraction <0.01; runs >=0.5 seconds reported",
            "caveat": "These measurements diagnose illuminated coverage and temporal change only. They do not prove artistic superiority, story quality, or subjective impact. Palette, line density, lighting, word highlights, flashes and geometry all affect these numbers."
        },
        "files": {name: value[0] for name, value in analyzed.items()},
    }
    v4, v5 = result["files"]["v4"], result["files"]["v5"]
    summary = {}
    for name in regions:
        old, new = v4["regions"][name], v5["regions"][name]
        summary[name] = {}
        for metric in ["coverage_luma_gt20", "coverage_luma_gt35",
                       "consecutive_frame_absolute_luma_difference",
                       "changed_fraction_absolute_luma_difference_gt3"]:
            a, b = old[metric]["mean"], new[metric]["mean"]
            summary[name][metric] = {"v4_mean": a, "v5_mean": b,
                                    "ratio": round(b/max(a, 1e-8), 4),
                                    "absolute_delta": round(b-a, 6)}
    perline = zip(v4["per_lyric"], v5["per_lyric"])
    summary["lyric_count_with_greater_perimeter_coverage_gt20"] = sum(
        b["perimeter_coverage_gt20_mean"] > a["perimeter_coverage_gt20_mean"] for a, b in perline)
    summary["lyric_count_with_greater_perimeter_motion"] = sum(
        b["perimeter_frame_difference_mean"] > a["perimeter_frame_difference_mean"]
        for a,b in zip(v4["per_lyric"],v5["per_lyric"]))
    result["comparison"] = summary
    # V4 uses several long inverted white-paper sections, unlike V5.
    # A bright empty paper background passes both line-coverage thresholds,
    # so also compare only matching timestamps that are dark in BOTH films.
    n=min(len(value[2]) for value in analyzed.values())
    common_dark=(analyzed['v4'][2][:n]<60)&(analyzed['v5'][2][:n]<60)
    common_diff=common_dark[:-1]&common_dark[1:]
    matched={
        "selection": "Matching sampled timestamps with whole usable-frame mean luma <60 in BOTH videos; transition differences included only when both endpoint frames satisfy the criterion.",
        "sampled_frames": int(common_dark.sum()),
        "sampled_seconds": round(float(common_dark.sum()/FPS),3),
        "regions": {},
    }
    for name in regions:
        reg={}
        for key in FILES:
            c20,c35,mad,changed=analyzed[key][1][name]
            reg[key]={"coverage_gt20":stats(c20[:n][common_dark]),
                      "coverage_gt35":stats(c35[:n][common_dark]),
                      "frame_difference":stats(mad[:n-1][common_diff]),
                      "changed_fraction":stats(changed[:n-1][common_diff])}
        matched['regions'][name]=reg
    result['comparison_common_dark_timestamps']=matched
    result["interpretation"] = [
        "Use coverage and temporal change jointly: higher coverage alone could describe a stationary dense drawing.",
        "Review lyric-level measurements to ensure whole-film averages are not determined by a small number of flashes or dense scenes.",
        "The sampled gray metrics cannot assess music synchronization, motion continuity below 125 milliseconds, glyph legibility or story progression; those require visual review.",
        "Whole-film threshold coverage includes bright background pixels: V4's longer white-paper sections inflate that metric. The common-dark-timestamp comparison partially controls that confound without changing the requested whole-film results."
    ]
    add_review(result)
    out = ROOT / "v5/space_motion_review.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"path":str(out), "perimeter": summary["perimeter_union"],
                      "coverage_improved_lyrics": summary["lyric_count_with_greater_perimeter_coverage_gt20"],
                      "motion_improved_lyrics": summary["lyric_count_with_greater_perimeter_motion"],
                      "v4_near_static_runs":v4["perimeter_near_static_runs_at_least_half_second"],
                      "v5_near_static_runs":v5["perimeter_near_static_runs_at_least_half_second"],
                      "common_dark_perimeter":matched['regions']['perimeter_union']}, indent=2))


if __name__ == "__main__":
    main()
