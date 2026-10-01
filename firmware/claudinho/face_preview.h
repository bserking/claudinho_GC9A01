#pragma once

// Browser previews mirror expressao(), desenhaOlho(), desenhaBoca() and extras().
static const char FACE_PREVIEW_JS[] PROGMEM = R"JS(
(() => {
  const names=['Sleeping','Neutral','Thinking','Working','Waiting for you','Done','Happy','Excited','Worried','Startled','Dizzy','Tired','Sweating','Angry','Sad','Suspicious'];
  let background='#f06818';
  const normal='#181818', blue='#488cd8', angry='#880808';
  function canvas(name,size=120){const c=document.createElement('canvas');c.width=c.height=240;c.className='face-preview';c.style.width=c.style.height=size+'px';c.dataset.face=String(names.indexOf(name));c.setAttribute('role','img');c.setAttribute('aria-label','Face: '+name);return c}
  function paint(c,phase){
    const id=Number(c.dataset.face);if(id<0)return;
    const ctx=c.getContext('2d');ctx.clearRect(0,0,240,240);ctx.save();ctx.beginPath();ctx.arc(120,120,120,0,2*Math.PI);ctx.clip();ctx.fillStyle=background;ctx.fillRect(0,0,240,240);
    const rect=(x,y,w,h,color=normal)=>{ctx.fillStyle=color;ctx.fillRect(Math.round(x*6),Math.round(y*8),Math.round(w*6),Math.round(h*8))};
    const eye=()=>({w:5,h:11,dx:0,dy:0,lid:0,bottom:0,chev:0,xis:false,diag:0,diagN:0});
    const l=eye(),r=eye();let mouth=0,color=normal;
    const both=o=>{Object.assign(l,o);Object.assign(r,o)},jump=(Math.floor(phase/2)&1)?-1:0;
    switch(id){
      case 0:both({lid:10,dy:2});break;
      case 2:both({dx:2,dy:-2});l.lid=1;r.lid=4;break;
      case 3:both({dx:(phase&1)?3:-3,h:7,dy:2});break;
      case 4:both({w:6,h:14});mouth=4;break;
      case 5:r.chev=1;break;
      case 6:both({chev:2,w:7,dy:jump});mouth=1;break;
      case 7:both({chev:1,h:13,dy:jump});mouth=2;break;
      case 8:both({diag:1,diagN:5,dy:2});mouth=5;break;
      case 9:both({w:8,h:16,dy:phase%16<2?-2:0});mouth=3;break;
      case 10:both({xis:true,w:7,h:7,bottom:(phase&1)?99:0});mouth=7;break;
      case 11:both({lid:5,dy:1});break;
      case 12:both({lid:5,diag:1,diagN:2,dy:1});mouth=7;break;
      case 13:both({diag:-1,diagN:5});l.dx=1;r.dx=-1;color=angry;mouth=6;if(phase%16<6){l.dx+=(phase&1)?1:-1;r.dx+=(phase&1)?1:-1}break;
      case 14:both({h:7,dy:4});l.dx=-1;r.dx=1;mouth=5;break;
      case 15:r.lid=5;l.w=6;l.h=12;both({dx:-2});mouth=8;break;
    }
    function drawEye(o,cx,left){
      const x=cx+o.dx-Math.floor(o.w/2),y=11+o.dy-Math.floor(o.h/2);
      if(o.chev===1){const n=o.h|1,mid=Math.floor(n/2),thick=o.w>=5?2:1,oy=y+Math.trunc((o.h-n)/2);for(let row=0;row<n;row++){const step=Math.abs(row-mid);rect(left?x+o.w-thick-step:x+step,oy+row,thick,1,color)}}
      else if(o.chev===2){const n=o.w|1,mid=Math.floor(n/2);for(let col=0;col<n;col++)rect(x+col,y+1+Math.abs(col-mid),1,2,color)}
      else if(o.xis){const n=Math.min(o.w,o.h)-1;if(o.bottom===99){rect(x+Math.floor(n/2),y,1,n,color);rect(x,y+Math.floor(n/2),n,1,color)}else for(let k=0;k<n;k++){rect(x+k,y+k,1,1,color);rect(x+n-1-k,y+k,1,1,color)}}
      else for(let row=0;row<o.h;row++){if(row<o.lid||row>=o.h-o.bottom)continue;let ext=o.w>=7&&(row===0||row===o.h-1)?1:0,inside=ext;if(row<o.diagN){if(o.diag>0)ext=Math.max(ext,o.diagN-row);else if(o.diag<0)inside=Math.max(inside,o.diagN-row)}const a=left?ext:inside,b=left?inside:ext;if(o.w-a-b>0)rect(x+a,y+row,o.w-a-b,1,color)}
    }
    drawEye(l,6,true);drawEye(r,34,false);
    const mouths=[[],[[15,21,1,1],[25,21,1,1],[16,22,1,1],[24,22,1,1],[17,23,7,1]],[[15,21,11,1],[16,22,9,2],[17,24,7,1]],[[18,21,5,4]],[[19,22,3,2]],[[17,21,7,1],[16,22,1,1],[24,22,1,1],[15,23,1,1],[25,23,1,1]],[[23,21,3,1],[19,22,4,1],[15,23,4,1]],[[15,21,2,1],[19,21,2,1],[23,21,2,1],[17,22,2,1],[21,22,2,1],[25,22,1,1]],[[16,22,9,1]]];
    mouths[mouth].forEach(v=>rect(...v));if(mouth===3)rect(19,22,3,2,background);
    const z=(x,y,u)=>{rect(x,y,5*u,u,'#884010');for(let k=0;k<3;k++)rect(x+(3-k)*u,y+(k+1)*u,u,u,'#884010');rect(x,y+4*u,5*u,u,'#884010')};
    if(id===0){const n=Math.floor(phase/4)%4;if(n>=1)z(14,9.5,.5);if(n>=2)z(17.5,5,.75);if(n>=3)z(22,0,1)}
    if(id===2)for(let k=0;k<Math.floor(phase/2)%4;k++)rect(17+k*3,4,1,1);
    if(id===4&&Math.floor(phase/2)%2===0)[[19,2,3,1],[18,3,1,1],[22,3,1,2],[21,5,1,1],[20,6,1,1],[20,8,1,1]].forEach(v=>rect(...v));
    if(id===9){rect(19,1,2,5);rect(19,7,2,1)}
    if(id===12){const q=phase%6;rect(38,2+q,1,2,blue);rect(37,4+q,3,2,blue);rect(38,6+q,1,1,blue)}
    if(id===14){const q=phase%8;rect(5,18+q,2,2,blue);rect(5,20+q,1,1,blue)}
    ctx.restore();
  }
  document.querySelectorAll('.face-card').forEach(card=>{const title=card.querySelector('strong');card.insertBefore(canvas(title.textContent),title)});
  const current=canvas('Sleeping',132);current.id='currentFacePreview';document.getElementById('face').before(current);
  window.facePreview={update(name,rgb){current.dataset.face=String(names.indexOf(name));current.setAttribute('aria-label','Current face: '+name);if(Number.isInteger(rgb)){const r=Math.round(((rgb>>11)&31)*255/31),g=Math.round(((rgb>>5)&63)*255/63),b=Math.round((rgb&31)*255/31);background=`rgb(${r},${g},${b})`}},history(name){return canvas(name,36)}};
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');let phase=0;
  const draw=()=>{document.querySelectorAll('canvas.face-preview').forEach(c=>paint(c,reduced.matches?10:phase));phase++};draw();setInterval(()=>{if(!document.hidden)draw()},250);
})();
)JS";
