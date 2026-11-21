"""Encode the six actual-result panels as a 30-second SILENT narration draft.
This is not the final submission: Aya must add her own recorded voice.
Requires opencv-python. Run from any directory with python encode_storyboard.py.
"""
from pathlib import Path
import json
import cv2

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'Mosaic_30_Seconds_SILENT_DRAFT.mp4'
durations = [6, 4, 4, 4, 8, 4]
fps = 30
writer = cv2.VideoWriter(str(DEST), cv2.VideoWriter_fourcc(*'mp4v'), fps, (1280, 720))
if not writer.isOpened():
    raise RuntimeError('The MP4 encoder is unavailable in this OpenCV build.')
try:
    for index, duration in enumerate(durations):
        frame = cv2.imread(str(ROOT / 'video_frames' / f'{index}.png'))
        if frame is None or frame.shape != (720, 1280, 3):
            raise ValueError('Unexpected storyboard frame: ' + str(index))
        for _ in range(duration * fps):
            writer.write(frame)
finally:
    writer.release()

capture = cv2.VideoCapture(str(DEST))
actual_fps = capture.get(cv2.CAP_PROP_FPS)
count = 0
dimensions = set()
while True:
    ok, frame = capture.read()
    if not ok:
        break
    count += 1
    dimensions.add((frame.shape[1], frame.shape[0]))
capture.release()
assert count == 900 and actual_fps == 30 and dimensions == {(1280, 720)}
metadata = {'file': DEST.name, 'frames_decoded': count, 'fps': actual_fps,
            'duration_seconds': count / actual_fps, 'dimensions': [1280, 720],
            'audio': 'NONE. Add Aya\'s own recorded narration before final submission.',
            'panel_duration_seconds': durations, 'opencv': cv2.__version__}
(ROOT / 'storyboard_video_validation.json').write_text(json.dumps(metadata, indent=2) + '\n')
print(json.dumps(metadata, indent=2))
