# Adaptive Mosaic Art

Aya Abdelkarem — CSc 8830 Computer Vision, Spring 2026

This working computer-vision art project converts photographs into adaptive rectangular mosaics. It allocates smaller tiles where a split most reduces color reconstruction error. Palette quantization and ink borders provide artistic controls.

## Run the demonstration

Download this repository using **Code → Download ZIP**, extract it, and open **demo.html** in a browser. Everything needed for the interactive demonstration is embedded in that file. Select a photograph, choose 64, 256 or 1,024 tiles, toggle palette/borders, and save the artwork. Personal images are processed in the browser and are not uploaded.

## Actual results

Nine equal-budget comparisons were executed on three credited example photographs. Adaptive tiles achieved lower unquantized RGB mean squared error than a regular grid in all nine comparisons.

| Photograph | MSE reduction at 256 tiles |
|---|---:|
| Astronaut | 14.96% |
| Coffee | 19.94% |
| Chelsea | 14.29% |

These are color-fidelity measurements before the palette/ink layer, not evidence of aesthetic preference. See `metrics.json` and `metrics.csv` for all nine measurements. Checks cover exact image coverage, tile count, monotonic error, independent raster error, constant images and quadrant images. The JavaScript core was cross-checked against Python.

## Files for review

- `Final_Project_Report.pdf`: problem, approach and results, followed by reproducibility and limitations.
- `Project_Pitch_One_Slide.pdf`: proposal.
- `Project_Updated_Pitch.pdf`: three-slide updated pitch.
- `Checkpoint_1_One_Page.pdf`: one page, three paragraphs.
- `GITHUB_LINK.txt`: the separate repository-link file required by the final submission.
- `Mosaic_30_Seconds_NARRATED.mp4`: completed 30-second video with Aya's recorded narration, synchronized project visuals, and verified H.264 video/AAC audio.
- `RECORDING_PLAN.md`: completed recording details and an explanation checklist.
- `demo.html`, `core.js`, `mosaic.py`: application and evaluation code.
- `project_resources.zip`: bundled `assets/`, `results/` and `video_frames/` folders, preserved together for reliable downloading; no trained model weights are needed. Run `python unpack_resources.py` to restore these folders. The browser demo already contains its images and does not need this step.

## Reproduce the numerical evaluation

Use a separate Python environment with NumPy and Pillow, then run:

```sh
python -m pip install -r requirements.txt
python unpack_resources.py
python mosaic.py
```

For a custom photograph:

```sh
python mosaic.py --image /path/to/photo.jpg --budget 256 --output custom_mosaic.png
```

The greedy split algorithm is not globally optimal. Tile budgets supported in the browser allow exact comparisons; arbitrary CLI budgets may stop at the nearest feasible quadtree leaf count (1 plus a multiple of 3). The uniform baseline and adaptive method receive identical 256×256 crops.

## Makeup status

The code, analysis, report, proposal and checkpoint materials are prepared. The final 30-second video now includes the student's own recorded voice, as required by the assignment. This is a newly prepared art-project direction; prior instructor acceptance has not been verified. The artifacts support asynchronous review and do not claim that an in-class demonstration took place. Nothing has been submitted or attached to Google Classroom.

Review the implementation and results before submission. See `ATTRIBUTION.md` for source-image credits.
