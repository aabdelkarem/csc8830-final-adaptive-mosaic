"""Build one self-contained HTML demo; uses only local included assets."""
from pathlib import Path
import base64,json
ROOT=Path(__file__).resolve().parent
assets={n:'data:image/png;base64,'+base64.b64encode((ROOT/'results'/(n+'_input.png')).read_bytes()).decode()
        for n in ['astronaut','coffee','chelsea']}
html=r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Adaptive Mosaic Art</title><style>
*{box-sizing:border-box}body{margin:0;background:#f7f3eb;color:#192331;font:17px/1.55 system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:40px 26px}h1{font-size:clamp(32px,5vw,56px);margin:0 0 8px;letter-spacing:-2px}h2{font-size:22px}p{max-width:850px}label{display:inline-block;margin:0 22px 16px 0}button,select,input::file-selector-button{font:inherit;background:white;border:1px solid #9baba9;padding:10px 14px;border-radius:5px;cursor:pointer}button:focus-visible,select:focus-visible{outline:3px solid #df6a32}button{background:#193e3d;color:white}input[type=file]{max-width:280px}section.controls{border-block:1px solid #bbc6c0;padding:20px 0;margin:28px 0}.views{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}canvas{width:100%;height:auto;image-rendering:pixelated;background:white}figure{margin:0}figcaption{font-weight:600;margin-bottom:10px}#result{padding:18px 0;color:#244d45;font-weight:600}small{color:#566564}details{border-top:1px solid #bbc6c0;padding:14px 0}summary{cursor:pointer;font-weight:600}@media(max-width:760px){.views{grid-template-columns:1fr}main{padding:25px 18px}h1{letter-spacing:-1px}}</style>
<main><h1>Adaptive Mosaic Art</h1><p>A photograph becomes a field of color tiles. Detailed regions receive smaller tiles, while smooth areas keep larger blocks.</p>
<section class="controls"><label>Photograph <select id="sample"><option>astronaut</option><option>coffee</option><option>chelsea</option></select></label><label>Tiles <select id="budget"><option>64</option><option selected>256</option><option>1024</option></select></label><label><input id="ink" type="checkbox" checked> Ink borders</label><label><input id="palette" type="checkbox" checked> Limited palette</label><br><label>Your photo <input type="file" id="file" accept="image/*"></label><button id="save">Save artwork</button></section>
<div class="views"><figure><figcaption>Original crop</figcaption><canvas id="original" width="256" height="256"></canvas></figure><figure><figcaption>Regular grid</figcaption><canvas id="regular" width="256" height="256"></canvas></figure><figure><figcaption>Adaptive mosaic</figcaption><canvas id="adaptive" width="256" height="256"></canvas></figure></div>
<p id="result" role="status" aria-live="polite">Loading the included photograph…</p>
<details open><summary>How the image guides the artwork</summary><p>Each tile uses its average RGB color. The algorithm considers splitting a tile into four quadrants and chooses the split that most reduces squared color error. It repeats until the tile budget is reached. Ink borders and the limited palette are artistic choices applied afterward.</p></details>
<details><summary>What the measurement means</summary><p>The displayed error compares the original crop with unrounded tile means before palette and border effects. Lower error means closer color reconstruction; it does not establish that people prefer the artwork. Both methods use the same crop and tile count. The Python report evaluates three included photographs, without a user study.</p></details>
<details><summary>Image credits and privacy</summary><p>NASA astronaut image (public domain); coffee by Rachel Michetti (CC0); Chelsea by Stefan van der Walt (CC0), distributed with scikit-image. See <a href="https://scikit-image.org/docs/stable/api/skimage.data.html">source documentation</a>. Personal photographs stay in this browser. This file has no remote scripts, analytics, model downloads, or upload service.</p></details><small>CSc 8830 Computer Vision • Working project draft for Aya Abdelkarem</small></main>
<script>const SAMPLES=__SAMPLES__;
__CORE__
const byId=id=>document.getElementById(id);let rgb,current;
function render(){
  const budget=Number(byId('budget').value); const result=mosaicCore(rgb,256,256,budget);
  const regular=[],n=Math.sqrt(budget),s=256/n;let uniformSSE=0;
  for(let y=0;y<256;y+=s)for(let x=0;x<256;x+=s){let color=[0,0,0];for(let j=y;j<y+s;j++)for(let i=x;i<x+s;i++)for(let c=0;c<3;c++)color[c]+=rgb[(j*256+i)*3+c]/(s*s);regular.push({box:[x,y,s,s],color});for(let j=y;j<y+s;j++)for(let i=x;i<x+s;i++)for(let c=0;c<3;c++)uniformSSE+=(rgb[(j*256+i)*3+c]-color[c])**2;}
  function draw(id,tiles){const ctx=byId(id).getContext('2d');for(const t of tiles){let color=t.color;if(byId('palette').checked)color=color.map(c=>Math.round(c/51)*51);ctx.fillStyle=`rgb(${color.join(',')})`;ctx.fillRect(...t.box);if(byId('ink').checked){ctx.strokeStyle='#181e2a';ctx.lineWidth=1;const[x,y,w,h]=t.box;ctx.strokeRect(x+.5,y+.5,w-1,h-1);}}}
  draw('regular',regular);draw('adaptive',result.tiles);const mse=uniformSSE/(256*256*3),reduction=100*(1-result.mse/mse);
  byId('result').textContent=`${result.tiles.length} tiles each · Adaptive color MSE ${result.mse.toFixed(2)} · Grid MSE ${mse.toFixed(2)} · ${Number.isFinite(reduction)?reduction.toFixed(1)+'% lower color error':'Uniform image: both errors are zero'}`;
}
async function show(src){const im=new Image();im.onload=()=>{const ctx=byId('original').getContext('2d');const side=Math.min(im.width,im.height);ctx.drawImage(im,(im.width-side)/2,(im.height-side)/2,side,side,0,0,256,256);const rgba=ctx.getImageData(0,0,256,256).data;rgb=new Float64Array(256*256*3);for(let i=0;i<256*256;i++)for(let c=0;c<3;c++)rgb[i*3+c]=rgba[i*4+c];render();};im.onerror=()=>byId('result').textContent='This photo could not be read. Try a JPG or PNG.';im.src=src;}
byId('sample').onchange=()=>show(SAMPLES[byId('sample').value]);for(const id of ['budget','ink','palette'])byId(id).onchange=render;
byId('file').onchange=e=>{const file=e.target.files[0];if(!file)return;const r=new FileReader();r.onload=()=>show(r.result);r.readAsDataURL(file);};
byId('save').onclick=()=>{const a=document.createElement('a');a.download='adaptive_mosaic.png';a.href=byId('adaptive').toDataURL('image/png');a.click();};show(SAMPLES.astronaut);
</script></html>'''
html=html.replace('__SAMPLES__',json.dumps(assets)).replace('__CORE__',(ROOT/'core.js').read_text())
(ROOT/'demo.html').write_text(html)
print('Created',ROOT/'demo.html')
