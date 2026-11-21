#!/usr/bin/env python3
"""Adaptive mosaic: reproducible computer-vision art without trained weights.

Each split replaces a rectangular constant-color region with four quadrants.
Choose the available split with greatest reduction in squared RGB error.
The greedy algorithm is not claimed globally optimal. All measurements use
unquantized mean colors; decorative ink/palette changes are evaluated separately.
"""
from pathlib import Path
import argparse, csv, hashlib, heapq, json, math, platform, time
import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent

def load(path):
    # Identical preprocessing for all methods: EXIF orientation then center crop.
    return np.asarray(ImageOps.fit(ImageOps.exif_transpose(Image.open(path)).convert('RGB'),
                                   (256,256), method=Image.Resampling.LANCZOS), dtype=float)

def integral(a):
    return np.pad(a.cumsum(0).cumsum(1), ((1,0),(1,0),(0,0)))

def region(total, box):
    x,y,w,h = box
    return total[y+h,x+w]-total[y,x+w]-total[y+h,x]+total[y,x]

def prepare(a):
    sums, squares = integral(a), integral(a*a)
    def stats(box):
        n=box[2]*box[3]; s=region(sums,box)
        return s/n, max(0.,float((region(squares,box)-s*s/n).sum()))
    return stats

def children(box):
    x,y,w,h=box
    if min(w,h)<2: return []
    a,b=w//2,h//2
    return [(x,y,a,b),(x+a,y,w-a,b),(x,y+b,a,h-b),(x+a,y+b,w-a,h-b)]

def adaptive(a,budget):
    if budget<1: raise ValueError('budget must be positive')
    h,w,_=a.shape; stats=prepare(a); root=(0,0,w,h)
    leaves={root}; heap=[]; trace=[stats(root)[1]]
    def push(box):
        cs=children(box)
        if cs:
            gain=max(0.,stats(box)[1]-sum(stats(c)[1] for c in cs))
            heapq.heappush(heap,(-gain,box))
    push(root)
    while heap and len(leaves)+3<=budget:
        ng,b=heapq.heappop(heap)
        leaves.remove(b); cs=children(b); leaves.update(cs)
        trace.append(trace[-1]+ng)
        for c in cs: push(c)
    ordered=sorted(leaves,key=lambda b:(b[1],b[0],b[2],b[3]))
    return [(b,stats(b)[0]) for b in ordered],trace

def uniform(a,budget):
    n=math.isqrt(budget)
    if n*n!=budget: raise ValueError('uniform budget must be a square')
    h,w,_=a.shape; stats=prepare(a); tiles=[]
    for j in range(n):
        for i in range(n):
            x,x2=i*w//n,(i+1)*w//n; y,y2=j*h//n,(j+1)*h//n
            b=(x,y,x2-x,y2-y); tiles.append((b,stats(b)[0]))
    return tiles

def raster(tiles,shape):
    a=np.zeros(shape,float); covered=np.zeros(shape[:2],np.uint8)
    for (x,y,w,h),color in tiles:
        a[y:y+h,x:x+w]=color; covered[y:y+h,x:x+w]+=1
    if not np.all(covered==1): raise AssertionError('Tiles overlap or leave gaps')
    return a

def art(tiles,shape):
    # Deliberate artistic layer: six levels/channel and fine dark tile borders.
    im=Image.new('RGB',(shape[1],shape[0])); draw=ImageDraw.Draw(im)
    for (x,y,w,h),color in tiles:
        c=tuple(np.clip(np.rint(color/51)*51,0,255).astype(int))
        draw.rectangle((x,y,x+w-1,y+h-1),fill=c,outline=(24,30,42),width=1)
    return im

def metrics(a,b):
    mse=float(np.mean((a-b)**2))
    return {'mse_rgb_0_255':mse,'psnr_db':float(10*np.log10(255**2/mse)) if mse else None}

def run():
    out=ROOT/'results';out.mkdir(exist_ok=True)
    rows=[]; predictions={}
    for name in ['astronaut','coffee','chelsea']:
        path=ROOT/'assets'/(name+'.png'); a=load(path)
        Image.fromarray(a.astype('uint8')).save(out/(name+'_input.png'))
        for budget in [64,256,1024]:
            t=time.perf_counter();tiles,trace=adaptive(a,budget);seconds=time.perf_counter()-t
            assert len(tiles)==budget
            assert np.max(np.diff(trace))<=1e-6
            b=raster(tiles,a.shape);u=raster(uniform(a,budget),a.shape)
            ma,mu=metrics(a,b),metrics(a,u)
            # Check independent raster error agrees with summed region errors.
            assert np.isclose(np.sum((a-b)**2),trace[-1],atol=1e-4,rtol=1e-10)
            row={'image':name,'budget':budget,'adaptive_mse':ma['mse_rgb_0_255'],
                 'uniform_mse':mu['mse_rgb_0_255'],'adaptive_psnr_db':ma['psnr_db'],
                 'uniform_psnr_db':mu['psnr_db'],
                 'mse_reduction_percent':100*(1-ma['mse_rgb_0_255']/mu['mse_rgb_0_255']),
                 'adaptive_seconds_single_run':seconds,'tile_count':len(tiles)}
            rows.append(row)
            if budget==256:
                Image.fromarray(np.rint(b).astype('uint8')).save(out/(name+'_adaptive.png'))
                Image.fromarray(np.rint(u).astype('uint8')).save(out/(name+'_uniform.png'))
                art(tiles,a.shape).save(out/(name+'_art.png'))
                predictions[name]=[{'box':list(box),'color':col.tolist()} for box,col in tiles]
    # Known cases exercise constant regions, borders and a split benefit.
    constant=np.full((16,16,3),77.)
    ct,_=adaptive(constant,16);assert np.array_equal(raster(ct,constant.shape),constant)
    quadrants=np.zeros((16,16,3));quadrants[:8,:8]=255;quadrants[8:,8:]=128
    qt,_=adaptive(quadrants,4);assert np.array_equal(raster(qt,quadrants.shape),quadrants)
    with open(out/'metrics.csv','w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    manifest={'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
       'python':platform.python_version(),'numpy':np.__version__,'rows':rows,
       'validation':'exact coverage, tile budgets, monotonic SSE, independent SSE, constant and quadrant checks passed',
       'preprocessing':'EXIF orientation, center crop and LANCZOS resize to 256x256, identical for both methods',
       'inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'assets').glob('*.png')}}
    (out/'metrics.json').write_text(json.dumps(manifest,indent=2))
    (out/'tiles.json').write_text(json.dumps(predictions))
    print(json.dumps({'validation':manifest['validation'],'results':rows},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',help='Optional personal photograph to turn into art')
    parser.add_argument('--budget',type=int,default=256)
    parser.add_argument('--output',default='custom_mosaic.png')
    args=parser.parse_args()
    if args.image:
        data=load(args.image);tiles,_=adaptive(data,args.budget)
        art(tiles,data.shape).save(args.output)
        print(f'Saved {args.output}; {len(tiles)} tiles')
    else: run()
