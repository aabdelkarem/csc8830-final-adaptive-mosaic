from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from mosaic import load,adaptive,art
ROOT=Path(__file__).resolve().parent
out=ROOT/'narrated_frames';out.mkdir(exist_ok=True)
def frame(i,title,subtitle,pictures):
    f=plt.figure(figsize=(12.8,7.2),dpi=100,facecolor='#fffdf9')
    f.text(.055,.92,title,color='#183c4a',fontsize=28,weight='bold')
    f.text(.055,.85,subtitle,color='#53626b',fontsize=17)
    for j,(image,label) in enumerate(pictures):
        width=.82/len(pictures);ax=f.add_axes([.07+j*(.88/len(pictures)),.18,width,.56]);ax.imshow(image);ax.axis('off');ax.set_title(label,fontsize=19,pad=12)
    f.text(.055,.07,'Adaptive Mosaic Art • Actual prototype outputs • Narration by Aya Abdelkarem',fontsize=13,color='#53626b')
    f.savefig(out/f'{i}.png',dpi=100);plt.close(f)
a=load(ROOT/'assets/coffee.png')
frame(0,'A photograph, a limited number of tiles','Regular grids use the same tile size in smooth and detailed regions.',[(a.astype('uint8'),'Original crop'),(Image.open(ROOT/'results/coffee_uniform.png'),'Regular grid: 256 tiles')])
for i,budget in [(1,64),(2,256),(3,1024)]:
    tiles,_=adaptive(a,budget)
    frame(i,f'Adaptive mosaic: {budget:,} tiles','Split the region that gives the largest reduction in squared color error.',[(art(tiles,a.shape),'Palette and ink artwork')])
frame(4,'Measured color-error reductions','256 tiles per method: astronaut 14.96%, coffee 19.94%, Chelsea 14.29%.',[(Image.open(ROOT/'results/astronaut_art.png'),'Astronaut'),(Image.open(ROOT/'results/coffee_art.png'),'Coffee'),(Image.open(ROOT/'results/chelsea_art.png'),'Chelsea')])
frame(5,'Color fidelity is one measure','Artistic preference needs a separate user study.',[(Image.open(ROOT/'results/coffee_art.png'),'Adaptive Mosaic Art')])
print(out)
