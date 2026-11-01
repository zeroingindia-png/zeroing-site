// Charts for The Other Details research pages. Each block draws into a #f-* element if present.
const F=id=>document.getElementById(id)||{set innerHTML(v){}};
const P='#f3efe6',RED='#e0505c',TEAL='#7fe3d6',GOLD='#f4b942',OFF='rgba(243,239,230,.16)',GRID='rgba(127,227,214,.22)';
const svg=(w,h,b)=>`<svg viewBox="0 0 ${w} ${h}" role="img">${b}</svg>`;
const T=(x,y,t,c='',a='start')=>`<text x="${x}" y="${y}" class="${c}" text-anchor="${a}">${t}</text>`;
const C=(x,y,r,f,o=1)=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${f}" opacity="${o}"/>`;
const L=(x1,y1,x2,y2,s,w=1,d='')=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${s}" stroke-width="${w}" ${d?`stroke-dasharray="${d}"`:''} stroke-linecap="round"/>`;
const $=id=>document.getElementById(id);
{let b='',S=30,y0=330;for(let j=0;j<25;j++)b+=C(20+(j%5)*S,y0-Math.floor(j/5)*S,10,P);
 for(let j=0;j<100;j++)b+=C(230+(j%10)*S,y0-Math.floor(j/10)*S,10,RED);
 b+=`<rect x="215" y="${y0-4*S-15}" width="${5*S}" height="${5*S}" fill="none" stroke="${TEAL}" stroke-width="2" rx="4"/>`;
 b+=L(5,y0+22,535,y0+22,TEAL,1.5)+T(80,y0+46,'2020','lab','middle')+T(365,y0+46,'2025','lab','middle')+T(80,y0-4*S-30,'375 MW','val','middle')+T(365,y0-9*S-30,'~1,500 MW','val','middle');
 b+=`<rect x="${290-34}" y="${y0-2*S-12}" width="68" height="24" rx="6" fill="#0b0c10" stroke="${TEAL}"/>`+T(290,y0-2*S+5,'= 2020','lab','middle');
 F('f-squares').innerHTML=svg(540,390,b)+'<div class="key">One dot = 15 MW</div>'}
{const X=y=>60+(y-2020)*38,Y=g=>300-g*10.5;let b='';[0,10,20].forEach(g=>{b+=L(50,Y(g),520,Y(g),GRID,g?1:1.5)+T(42,Y(g)+4,g+' GW','','end')});
 [2020,2025,2030,2032].forEach(y=>b+=T(X(y),324,y===2032?'FY32':y,'lab','middle'));
 b+=L(X(2020),Y(.375),X(2025),Y(1.5),P,3)+C(X(2020),Y(.375),5,P)+C(X(2025),Y(1.5),7,P)+T(X(2025)+12,Y(1.5)+20,'1.5 GW today');
 b+=L(X(2025),Y(1.5),X(2030),Y(4.5),GOLD,2,'4 6')+L(X(2025),Y(1.5),X(2030),Y(6.5),GOLD,2,'4 6')+`<rect x="${X(2030)-6}" y="${Y(6.5)}" width="12" height="${Y(4.5)-Y(6.5)}" fill="${GOLD}" opacity=".5" rx="4"/>`+T(X(2030)+14,Y(6.5)+14,'4.5–6.5 GW','lab')+T(X(2030)+14,Y(6.5)+32,'CEEW');
 b+=L(X(2025),Y(1.5),X(2032),Y(26.3),RED,2,'4 6')+C(X(2032),Y(26.3),8,RED)+T(X(2032)-14,Y(26.3)-14,'+26.3 GW · power ministry, 2026','lab','end');
 F('f-fan').innerHTML=svg(540,340,b)}
{let b='';for(let j=0;j<150;j++)b+=C(14+(j%15)*36,14+Math.floor(j/15)*36,11,j<148?P:OFF);
 F('f-people').innerHTML=svg(540,366,b)+'<div class="key">20 lakh L ÷ 135 L ≈ 15,000 people · one dot = 100 people</div>'}
{let b='';const w=(x0,on,col)=>{for(let j=0;j<100;j++)b+=C(x0+(j%10)*24,14+Math.floor(j/10)*24,8,j<on?col:OFF)};w(10,18,P);w(290,4,TEAL);
 b+=T(10,292,'18%','val')+T(10,314,'of the world’s people')+T(290,292,'4%','val')+T(290,314,'of its fresh water');
 F('f-waffles').innerHTML=svg(540,322,b)+'<div class="key">Each grid: 100 dots = the world total</div>'}
{let b='';const row=(y,lab,v,col,txt)=>{b+=T(0,y-12,lab,'lab')+`<rect x="0" y="${y}" width="360" height="22" fill="${OFF}" rx="4"/>`+`<rect x="0" y="${y}" width="${3.6*v}" height="22" fill="${col}" rx="4"/>`+T(3.6*Math.max(v,100)+10,y+18,txt,'val')};
 row(40,'Tonnes bought · 2024 = 100',89,P,'89');row(130,'Rupees spent · 2024 = 100',130,GOLD,'130');b+=L(360,20,360,170,TEAL,1.5,'3 5')+T(360,192,'2024 level','','middle');
 F('f-paradox').innerHTML=svg(560,200,b)+'<div class="key">710.9 t vs 802.8 t · ₹7.51 vs ₹5.76 lakh crore</div>'}
{let b='',S=22;for(let j=0;j<223;j++){const s=j<25,f=j>=25&&j<35;b+=C(10+(j%22)*S,10+Math.floor(j/22)*S,7,s||f?GOLD:OFF,f?.45:1)}
 b+=T(0,252,'All gold ever mined ≈ 222,600 t','lab')+T(0,272,'Indian homes: 25,000 t (solid) to 34,600 t (faded) · RBI 880 t, under one dot');
 F('f-stock').innerHTML=svg(500,284,b)+'<div class="key">One dot = 1,000 tonnes</div>'}
