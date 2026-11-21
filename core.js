/* Adaptive color-region partitioning. Browser and Node share this exact code. */
function mosaicCore(rgb, width, height, budget) {
  const stride=width+1, size=(height+1)*stride*3;
  const sums=new Float64Array(size), squares=new Float64Array(size);
  for(let y=1;y<=height;y++)for(let x=1;x<=width;x++)for(let c=0;c<3;c++){
    const p=(y*stride+x)*3+c, value=rgb[((y-1)*width+x-1)*3+c];
    sums[p]=value+sums[p-3]+sums[p-stride*3]-sums[p-stride*3-3];
    squares[p]=value*value+squares[p-3]+squares[p-stride*3]-squares[p-stride*3-3];
  }
  function stat(b){
    const [x,y,w,h]=b, n=w*h, color=[]; let sse=0;
    for(let c=0;c<3;c++){
      const idx=(xx,yy)=>(yy*stride+xx)*3+c;
      const sum=t=>t[idx(x+w,y+h)]-t[idx(x,y+h)]-t[idx(x+w,y)]+t[idx(x,y)];
      const s=sum(sums);color.push(s/n);sse+=sum(squares)-s*s/n;
    }
    return {box:b,color,sse:Math.max(0,sse)};
  }
  function split(tile){
    const [x,y,w,h]=tile.box;if(Math.min(w,h)<2)return null;
    const a=Math.floor(w/2),b=Math.floor(h/2);
    const children=[[x,y,a,b],[x+a,y,w-a,b],[x,y+b,a,h-b],[x+a,y+b,w-a,h-b]].map(stat);
    return {tile,children,gain:Math.max(0,tile.sse-children.reduce((s,t)=>s+t.sse,0))};
  }
  const root=stat([0,0,width,height]), leaves=new Set([root]);
  const candidates=[];const offer=t=>{const s=split(t);if(s)candidates.push(s);};offer(root);
  while(candidates.length && leaves.size+3<=budget){
    candidates.sort((a,b)=>{let d=a.gain-b.gain;if(d)return d;for(let i=0;i<4;i++){d=b.tile.box[i]-a.tile.box[i];if(d)return d;}return 0;});
    const next=candidates.pop();leaves.delete(next.tile);
    for(const t of next.children){leaves.add(t);offer(t);}
  }
  const tiles=[...leaves];
  return {tiles,mse:tiles.reduce((s,t)=>s+t.sse,0)/(width*height*3)};
}
if(typeof module!=='undefined')module.exports={mosaicCore};
