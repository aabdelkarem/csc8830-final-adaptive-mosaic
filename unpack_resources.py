"""Extract the bundled public images and saved results beside this script."""
from pathlib import Path
from zipfile import ZipFile

root = Path(__file__).resolve().parent
with ZipFile(root / 'project_resources.zip') as archive:
    for member in archive.infolist():
        target = (root / member.filename).resolve()
        if root not in target.parents:
            raise ValueError('Unsafe archive path')
        if target.exists() and target.is_file() and target.read_bytes() != archive.read(member):
            raise FileExistsError(f'Preserving modified file: {target}; extract into a fresh folder instead.')
    archive.extractall(root)
print('Extracted assets/, results/ and video_frames/.')
