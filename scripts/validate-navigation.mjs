import fs from 'node:fs';import assert from 'node:assert/strict';import ts from 'typescript';
const source=ts.transpileModule(fs.readFileSync('lib/navigation.ts','utf8'),{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;
const {inPolygon,canWalkAt}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const data=JSON.parse(fs.readFileSync('public/models/daylight/collision.json'));
const manifest=JSON.parse(fs.readFileSync('public/daylight-tour/manifest.json'));
for(const v of manifest.views){assert(canWalkAt(data,v.position[0],v.position[2]),`Blocked panorama position: ${v.id}`);for(const id of v.links)assert(manifest.views.some(x=>x.id===id),`Broken room link ${id}`);}
// Check graph traversal reaches every supplied room from the initial viewpoint.
const seen=new Set(['living']),queue=['living'];while(queue.length){const next=queue.shift(),v=manifest.views.find(v=>v.id===next);for(const id of v.links)if(!seen.has(id)){seen.add(id);queue.push(id);}}
assert.equal(seen.size,manifest.views.length);
assert(!canWalkAt(data,8,6));assert(!canWalkAt(data,4.1,11));assert(!canWalkAt(data,5.9,6.7));
// Flood-fill the actual solid collision model to verify passage through interior doorways.
const step=.09,minX=-.6,minZ=-4.3,nx=90,nz=195,key=(i,j)=>j*nx+i;
const grid=new Uint8Array(nx*nz);for(let j=0;j<nz;j++)for(let i=0;i<nx;i++)grid[key(i,j)]=canWalkAt(data,minX+i*step,minZ+j*step)?1:0;
const start=[Math.round((6.35-minX)/step),Math.round((1.25-minZ)/step)],todo=[start];grid[key(...start)]=2;
for(let n=0;n<todo.length;n++){const[i,j]=todo[n];for(const[dx,dz]of[[1,0],[-1,0],[0,1],[0,-1]]){const a=i+dx,b=j+dz;if(a>=0&&a<nx&&b>=0&&b<nz&&grid[key(a,b)]===1){grid[key(a,b)]=2;todo.push([a,b]);}}}
const reached=[];for(const [id,polygon] of Object.entries(data.rooms)){if(['deck','laundry'].includes(id))continue;assert(todo.some(([i,j])=>inPolygon(minX+i*step,minZ+j*step,polygon)),`No continuous interior path to ${id}`);reached.push(id);}
console.log(JSON.stringify({tourViewpoints:seen.size,solidObstacles:data.solids.length,continuousRooms:reached},null,2));
