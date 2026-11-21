"""Combine Aya's recorded narration with the actual project output panels."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import tempfile

import av
import cv2
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
FPS = 30
TOTAL_SECONDS = 30


def main(recording, timing_file):
    timing = json.loads(Path(timing_file).read_text())
    words = [word for segment in timing['segments'] for word in segment['words']]
    tokens = [re.sub(r'[^a-z]', '', word['word'].lower()) for word in words]
    with av.open(str(recording)) as source:
        stream = source.streams.audio[0]
        sample_rate = stream.codec_context.sample_rate
        samples = sum(frame.samples for frame in source.decode(audio=0))
    source_duration = samples / sample_rate
    trim_start = max(0.0, words[0]['start'] - 0.2)
    trim_end = min(source_duration, words[-1]['end'] + 0.25)
    speech_window = 29.6
    tempo = (trim_end - trim_start) / speech_window

    def phrase_time(phrase):
        wanted = phrase.split()
        for index in range(len(tokens) - len(wanted) + 1):
            if tokens[index:index + len(wanted)] == wanted:
                return 0.2 + (words[index]['start'] - trim_start) / tempo
        raise ValueError('Could not align narration phrase: ' + phrase)

    boundaries = [0, phrase_time('it repeatedly'), phrase_time('giving detailed'),
                  phrase_time('users can'), phrase_time('on three'),
                  phrase_time('these results'), TOTAL_SECONDS]
    frame_boundaries = [round(value * FPS) for value in boundaries]
    assert frame_boundaries == sorted(frame_boundaries)
    output = ROOT / 'Mosaic_30_Seconds_NARRATED.mp4'
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.TemporaryDirectory(prefix='aya-narrated-render-') as temp:
        silent = Path(temp) / 'visuals.mp4'
        writer = imageio_ffmpeg.write_frames(str(silent), (1280, 720), fps=FPS,
                                             codec='libx264', quality=8,
                                             macro_block_size=1, pix_fmt_in='rgb24')
        writer.send(None)
        for index in range(6):
            panel = cv2.imread(str(ROOT / 'narrated_frames' / f'{index}.png'))
            assert panel is not None and panel.shape == (720, 1280, 3)
            rgb = cv2.cvtColor(panel, cv2.COLOR_BGR2RGB)
            for _ in range(frame_boundaries[index + 1] - frame_boundaries[index]):
                writer.send(rgb)
        writer.close()
        audio_filter = (
            f'atrim=start={trim_start:.6f}:end={trim_end:.6f},asetpts=PTS-STARTPTS,'
            f'atempo={tempo:.9f},loudnorm=I=-16:TP=-1.5:LRA=11,'
            'aresample=48000,adelay=200|200,apad,atrim=duration=30,alimiter=limit=0.8:level=disabled'
        )
        command = [ffmpeg, '-y', '-hide_banner', '-loglevel', 'error',
                   '-i', str(silent), '-i', str(recording),
                   '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
                   '-af', audio_filter, '-c:a', 'aac', '-b:a', '192k',
                   '-t', '30', '-movflags', '+faststart', str(output)]
        subprocess.run(command, check=True)

    with av.open(str(output)) as final:
        assert len(final.streams.video) == 1 and len(final.streams.audio) == 1
        video_stream = final.streams.video[0]
        assert video_stream.width == 1280 and video_stream.height == 720
        assert float(video_stream.average_rate) == FPS
        video_frames = sum(1 for _ in final.decode(video=0))
    assert video_frames == 900
    with av.open(str(output)) as final:
        audio_samples = sum(frame.samples for frame in final.decode(audio=0))
    subprocess.run([ffmpeg, '-v', 'error', '-i', str(output), '-f', 'null', '-'], check=True)
    validation = {
        'file': output.name,
        'duration_seconds': TOTAL_SECONDS,
        'decoded_video_frames': video_frames,
        'fps': FPS,
        'dimensions': [1280, 720],
        'decoded_audio_samples_per_channel': audio_samples,
        'audio_sample_rate': 48000,
        'source_recording_sha256': hashlib.sha256(Path(recording).read_bytes()).hexdigest(),
        'source_recording_decoded_seconds': source_duration,
        'source_trim_start_seconds': trim_start,
        'source_trim_end_seconds': trim_end,
        'pitch_preserving_tempo_factor': tempo,
        'panel_boundaries_seconds': [frame / FPS for frame in frame_boundaries],
        'audio_processing': 'Recorded voice, pitch-preserving tempo adjustment, loudness normalization, 0.2-second lead-in.',
        'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'audio_origin': 'User-uploaded New Recording(2).m4a',
    }
    (ROOT / 'narrated_video_validation.json').write_text(json.dumps(validation, indent=2) + '\n')
    print(json.dumps(validation, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('recording', type=Path)
    parser.add_argument('timing_file', type=Path)
    args = parser.parse_args()
    main(args.recording, args.timing_file)
