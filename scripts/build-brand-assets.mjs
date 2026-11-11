// Offline source-only asset builder. Runtime users consume the generated files.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url);
const sharp=require(process.env.COLVIA_SHARP_MODULE || 'sharp');
if(sharp.versions.sharp!=='0.35.5') throw Error('Use sharp 0.35.5 for this asset revision');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=path.join(root,'assets/brand/source');
const out=process.argv[2] ? path.resolve(process.argv[2]) : path.join(root,'assets/brand');
const geometry=JSON.parse(fs.readFileSync(path.join(source,'geometry.json')));
const hash=b=>createHash('sha256').update(b).digest('hex');
if(hash(fs.readFileSync(path.join(source,'r6-1-open-c.svg')))!=='3ad729a48ea40a9927b49a1b68826485d1ca514397050a89f7679fd59a193dd9') throw Error('Selected symbol changed');
const files={};
function put(name,data){const p=path.join(out,name);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,data);files[name]={sha256:hash(data),bytes:Buffer.byteLength(data)};}
function svg(w,h,body,label='Colvia'){return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" role="img" aria-label="${label}">${body}</svg>\n`;}
function symbol(c){return `<path fill="${c}" d="${geometry.symbol.path}"/>`;}
function glyph(k,x,y,size,c){return `<path fill="${c}" transform="translate(${x} ${y}) scale(${size/64})" d="${geometry[k].path}"/>`;}
for(const [name,color] of Object.entries({light:'#1F5F5B',dark:'#8CC6BC',black:'#000000',white:'#FFFFFF',current:'currentColor'})) put(`symbol-${name}.svg`,svg(64,64,symbol(color)));
for(const [theme,colors] of Object.entries({light:['#1F5F5B','#1E2A28'],dark:['#8CC6BC','#ECE6DA']})){
 for(const intro of [false,true]){
  const width=Math.ceil(Math.max(100+geometry.colvia.advance*42/64, intro?100+geometry.descriptor.advance*14/64:0)+20);
  const body=`<g transform="translate(4 6) scale(1.3125)">${symbol(colors[0])}</g>`+glyph('colvia',100,intro?51:61,42,colors[1])+(intro?glyph('descriptor',100,75,14,colors[1]):'');
  const name=`${intro?'logo-intro':'logo'}-${theme}`;
  const data=svg(width,96,body,intro?'Colvia — AI Work Harness':'Colvia');put(name+'.svg',data);
  put(name+'.png',await sharp(Buffer.from(data), {density:144}).resize(width*2,192).png().toBuffer());
 }
}
// README hero: center actual symbol ink against the complete two-line text block.
for(const [theme,colors] of Object.entries({light:['#1F5F5B','#1E2A28'],dark:['#8CC6BC','#ECE6DA']})){
 const sb=geometry.symbol.bounds,cb=geometry.colvia.bounds,db=geometry.descriptor.bounds;
 const cs=48/64,ds=14/64,ch=cb[3]*cs,dh=db[3]*ds,gapY=11,blockH=ch+gapY+dh;
 const ss=blockH/sb[3],symbolW=sb[2]*ss,textW=Math.max(cb[2]*cs,db[2]*ds),gapX=24;
 const width=Math.ceil(symbolW+gapX+textW+40),height=104,left=(width-symbolW-gapX-textW)/2,top=(height-blockH)/2;
 const b=`<path fill="${colors[0]}" transform="translate(${left-sb[0]*ss} ${top-sb[1]*ss}) scale(${ss})" d="${geometry.symbol.path}"/>`
  +`<path fill="${colors[1]}" transform="translate(${left+symbolW+gapX-cb[0]*cs} ${top-cb[1]*cs}) scale(${cs})" d="${geometry.colvia.path}"/>`
  +`<path fill="${colors[1]}" transform="translate(${left+symbolW+gapX-db[0]*ds} ${top+ch+gapY-db[1]*ds}) scale(${ds})" d="${geometry.descriptor.path}"/>`;
 const name=`logo-hero-${theme}`,data=svg(width,height,b,'Colvia — AI Work Harness');put(name+'.svg',data);
 put(name+'.png',await sharp(Buffer.from(data),{density:144}).resize(width*2,height*2).png().toBuffer());
}
const [x,y,w,h]=geometry.symbol.bounds,s=72/w,dx=64-s*(x+w/2),dy=64-s*(y+h/2);
const icon=svg(128,128,`<rect width="128" height="128" rx="28.8" fill="#1F5F5B"/><g transform="translate(${dx} ${dy}) scale(${s})">${symbol('#F6F1E7')}</g>`);
put('icon.svg',icon);
const rasters=new Map();
for(const n of [16,20,24,32,40,48,64,128,256,512,1024]){const png=await sharp(Buffer.from(icon), {density:Math.max(72, Math.ceil(72*n/128))}).resize(n,n).png().toBuffer();rasters.set(n,png);put(`png/icon-${n}.png`,png);}
for(const color of ['black','white'])for(const n of [16,32]) put(`png/symbol-${color}-${n}.png`,await sharp(Buffer.from(svg(64,64,symbol(color==="black"?'#000000':'#FFFFFF')))).resize(n,n).png().toBuffer());
// ICO directory with PNG image payloads; no OS-dependent encoder or metadata.
const sizes=[16,20,24,32,40,48,64,256],header=Buffer.alloc(6+16*sizes.length);header.writeUInt16LE(1,2);header.writeUInt16LE(sizes.length,4);
let offset=header.length;for(const [i,n] of sizes.entries()){const at=6+i*16,b=rasters.get(n);header[at]=header[at+1]=n===256?0:n;header.writeUInt16LE(1,at+4);header.writeUInt16LE(32,at+6);header.writeUInt32LE(b.length,at+8);header.writeUInt32LE(offset,at+12);offset+=b.length;}
put('colvia.ico',Buffer.concat([header,...sizes.map(n=>rasters.get(n))]));
// Modern macOS ICNS types contain complete PNGs (including Retina variants).
const chunks=[];for(const [type,n] of Object.entries({icp4:16,icp5:32,icp6:64,ic07:128,ic08:256,ic09:512,ic10:1024,ic11:32,ic12:64,ic13:256,ic14:512})){const b=rasters.get(n),h=Buffer.alloc(8);h.write(type);h.writeUInt32BE(b.length+8,4);chunks.push(h,b);}
const ih=Buffer.alloc(8);ih.write('icns');ih.writeUInt32BE(8+chunks.reduce((a,b)=>a+b.length,0),4);put('colvia.icns',Buffer.concat([ih,...chunks]));
const inputs={};for(const n of ['geometry.json','r6-1-open-c.svg','Inter-SemiBold.otf','Inter-Medium.otf','LICENSE.txt'])inputs[n]=hash(fs.readFileSync(path.join(source,n)));
put('manifest.json',JSON.stringify({schema:1,selection:'R6-1 Open C',name:'Colvia',descriptor:'AI Work Harness',palette:{teal:'#1F5F5B',ivory:'#F6F1E7',mint:'#8CC6BC'},renderer:sharp.versions,inputs,files},null,2)+'\n');
console.log(JSON.stringify({files:Object.keys(files).length,output:out}));
