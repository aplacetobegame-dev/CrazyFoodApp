"""Check a rebuilt export, or pass the path of an approved final to verify it."""
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent


def verify(path):
    probe = json.loads(subprocess.check_output([
        shutil.which('ffprobe'), '-v', 'error', '-show_streams', '-show_format',
        '-of', 'json', str(path)], text=True))
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    audio = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    duration = float(probe['format']['duration'])
    assert abs(duration - 25) < .025, duration
    assert (video['width'], video['height']) == (1080, 1920), video
    assert video['avg_frame_rate'] == '30/1' and int(video['nb_frames']) == 750, video
    assert audio['sample_rate'] == '48000' and audio['channels'] == 2, audio
    decode = subprocess.run([
        shutil.which('ffmpeg'), '-hide_banner', '-loglevel', 'error', '-i', str(path),
        '-f', 'null', '-'], capture_output=True, text=True, check=True)
    assert not decode.stderr.strip(), decode.stderr
    levels = subprocess.run([
        shutil.which('ffmpeg'), '-hide_banner', '-i', str(path), '-af', 'volumedetect',
        '-vn', '-sn', '-dn', '-f', 'null', '-'], capture_output=True, text=True, check=True)
    peak = float(re.search(r'max_volume: ([\d.-]+)', levels.stderr).group(1))
    assert peak < -.2, peak
    return {'verified': True, 'file': str(path.resolve()), 'duration_seconds': duration,
            'width': 1080, 'height': 1920, 'frames': 750, 'fps': 30,
            'audio_sample_rate': 48000, 'channels': 2, 'audio_peak_dbfs': peak,
            'decode_errors': False, 'size_bytes': path.stat().st_size}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', nargs='?', type=Path,
                        default=ROOT/'build/food-felonies-breakfast-final-boss-25s.mp4')
    args = parser.parse_args()
    report = verify(args.video)
    (ROOT/'build').mkdir(parents=True, exist_ok=True)
    (ROOT/'build/verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
