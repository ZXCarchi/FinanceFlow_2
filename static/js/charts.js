(() => {
  const c=document.getElementById('trendChart'); if(!c) return;
  let data=[]; try{data=JSON.parse(c.dataset.trend||'[]')}catch{}
  const ctx=c.getContext('2d'); const dpr=window.devicePixelRatio||1;
  function draw(){
    const rect=c.getBoundingClientRect(); c.width=rect.width*dpr; c.height=240*dpr; ctx.scale(dpr,dpr);
    const w=rect.width,h=240,p={l:38,r:16,t:18,b:34}; ctx.clearRect(0,0,w,h);
    if(!data.length) return;
    const max=Math.max(1,...data.flatMap(x=>[x.income,x.expense]));
    ctx.font='10px system-ui';ctx.fillStyle='#7b8494';ctx.strokeStyle='#e9ecf2';ctx.lineWidth=1;
    for(let i=0;i<=4;i++){const y=p.t+(h-p.t-p.b)*i/4;ctx.beginPath();ctx.moveTo(p.l,y);ctx.lineTo(w-p.r,y);ctx.stroke();const v=Math.round(max*(1-i/4));ctx.fillText(v.toLocaleString(),2,y+3)}
    const group=(w-p.l-p.r)/data.length; const bw=Math.min(24,group*.27);
    data.forEach((d,i)=>{const x=p.l+group*i+group/2; const ih=(h-p.t-p.b)*(d.income/max); const eh=(h-p.t-p.b)*(d.expense/max);
      let g=ctx.createLinearGradient(0,p.t,0,h-p.b);g.addColorStop(0,'#6d5ce7');g.addColorStop(1,'#9d91f3');ctx.fillStyle=g;ctx.fillRect(x-bw-2,h-p.b-ih,bw,ih);
      let g2=ctx.createLinearGradient(0,p.t,0,h-p.b);g2.addColorStop(0,'#13b89b');g2.addColorStop(1,'#86dfcf');ctx.fillStyle=g2;ctx.fillRect(x+2,h-p.b-eh,bw,eh);
      ctx.fillStyle='#737c8c';ctx.textAlign='center';ctx.fillText(d.label,x,h-12);
    });ctx.textAlign='start';
  }
  draw(); addEventListener('resize',draw);
})();
