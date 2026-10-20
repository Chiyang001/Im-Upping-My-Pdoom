"""Standard-library-only CLI setup, before fonts, geometry or OpenGL load."""

import argparse
import os
from pathlib import Path


PREVIEW_FLAGS = (
    'metaphor_preview', 'v13_preview', 'flight_preview', 'ferocity_preview',
    'angles_preview', 'words_preview', 'impact_preview', 'edits', 'audit',
    'preview', 'meaning_preview',
)
SOURCE_NAME = '\u5413\u54ed\u4e86Opus5.5 AGI\u6982\u5ff5MV.mp4'
OUTPUT_NAME = 'Im_Upping_My_Pdoom_Meaning_in_Motion_1080p.mp4'


def _absolute(value, invocation_dir):
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (invocation_dir / path).resolve()


def parse_render_options(root, argv=None, require_audio=True):
    """Resolve inputs without importing any rendering dependency.

    Explicit paths are relative to the caller's working directory. Built-in
    defaults are relative to the repository, so an absolute script invocation
    works from outside the checkout as well.
    """
    root = Path(root).resolve()
    invocation_dir = Path.cwd()
    parser = argparse.ArgumentParser(
        description='Render the procedural wireframe P(doom) music video.',
        epilog='Previews need a font and OpenGL 3.3, but no audio. '
               'Command-line paths override PDOOM_AUDIO, PDOOM_FONT, '
               'PDOOM_OUTPUT and PDOOM_BACKEND environment variables.',
    )
    parser.add_argument('--audio', metavar='FILE', default=os.environ.get('PDOOM_AUDIO'),
                        help='audio/video source to copy the soundtrack from (PDOOM_AUDIO)')
    parser.add_argument('--font', metavar='FILE', default=os.environ.get('PDOOM_FONT'),
                        help='TrueType/OpenType font file (PDOOM_FONT; defaults to system bold sans)')
    parser.add_argument('--output', metavar='FILE', default=os.environ.get('PDOOM_OUTPUT'),
                        help='MP4 output file (PDOOM_OUTPUT)')
    parser.add_argument('--backend', default=os.environ.get('PDOOM_BACKEND') or None,
                        help='ModernGL context backend, such as egl; default uses the platform backend (PDOOM_BACKEND)')
    parser.add_argument('--sample', type=float, metavar='SECONDS',
                        help='render a short sample starting at this timestamp')
    parser.add_argument('--duration', type=float, default=12, metavar='SECONDS',
                        help='sample duration (default: 12 seconds)')
    previews = parser.add_argument_group('existing previews and diagnostics')
    for flag in PREVIEW_FLAGS:
        previews.add_argument('--' + flag.replace('_', '-'), action='store_true')
    args = parser.parse_args(argv)

    if args.sample is not None and not 0 <= args.sample < 156.667:
        parser.error('--sample must be at least 0 and less than 156.667 seconds')
    if args.duration <= 0:
        parser.error('--duration must be greater than 0')

    if args.font:
        args.font = _absolute(args.font, invocation_dir)
        if not args.font.is_file():
            parser.error(f'Font file does not exist: {args.font}')
    else:
        windows_dir = Path(os.environ.get('WINDIR', 'C:/Windows'))
        candidates = [
            windows_dir / 'Fonts/arialbd.ttf',
            Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'),
            Path('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'),
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
            Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf'),
            Path('/Library/Fonts/Arial Bold.ttf'),
        ]
        args.font = next((p.resolve() for p in candidates if p.is_file()), None)
        if args.font is None:
            parser.error('No supported system font found. Pass --font /path/to/font.ttf '
                         'or set PDOOM_FONT. Fonts are not included in this repository.')

    args.preview_only = any(getattr(args, flag) for flag in PREVIEW_FLAGS)
    if require_audio and not args.preview_only:
        if args.audio:
            args.audio = _absolute(args.audio, invocation_dir)
            if not args.audio.is_file():
                parser.error(f'Audio/video source does not exist: {args.audio}')
        elif (root / SOURCE_NAME).is_file():
            args.audio = root / SOURCE_NAME
        else:
            sources = sorted(root.glob('*.mp4'))
            if len(sources) != 1:
                detail = 'No source MP4 was found' if not sources else 'Multiple source MP4 files were found'
                parser.error(detail + '. Pass --audio FILE or set PDOOM_AUDIO. '
                             'The soundtrack is not included in this repository.')
            args.audio = sources[0].resolve()
    else:
        # Still previews and imported geometry diagnostics do not use audio.
        args.audio = None

    if args.output:
        args.output = _absolute(args.output, invocation_dir)
    elif args.sample is not None:
        args.output = root / 'v15' / f'sample-{int(args.sample)}.mp4'
    else:
        args.output = root / 'output_v15' / OUTPUT_NAME
    if args.audio is not None and args.output == args.audio:
        parser.error('--output must differ from the audio/video source')
    return args
