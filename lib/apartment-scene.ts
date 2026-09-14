import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { rooms, floorRects, type Mode } from './apartment-data';

type Rect = {x0:number;x1:number;z0:number;z1:number};
export function createApartment(host:HTMLDivElement,onRoom:(id:string)=>void,onReady:()=>void) {
 const planScale=1.0441; // Approximate gross footprint normalized to 1,140 sq ft; no measured dimensions supplied.
 const scene=new THREE.Scene(); scene.background=new THREE.Color('#d5dde0');
 const camera=new THREE.PerspectiveCamera(66,1,.035,160); camera.rotation.order='YXZ';
 const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
 renderer.setPixelRatio(Math.min(window.devicePixelRatio,1.8)); renderer.shadowMap.enabled=true;
 renderer.shadowMap.type=THREE.PCFSoftShadowMap; renderer.toneMapping=THREE.ACESFilmicToneMapping;
 renderer.toneMappingExposure=1.05; renderer.localClippingEnabled=true; host.appendChild(renderer.domElement);
 renderer.domElement.setAttribute('aria-label','Interactive 3D apartment. Drag to look around; use W A S D or the movement buttons to walk.');
 const env=new RoomEnvironment(); const pmrem=new THREE.PMREMGenerator(renderer);const envTarget=pmrem.fromScene(env,.04);scene.environment=envTarget.texture;env.dispose();pmrem.dispose();
 const architecture=new THREE.Group(),ceilings=new THREE.Group(),decor=new THREE.Group(); scene.add(architecture,ceilings,decor);
 const colliders:Rect[]=[];const cutMaterials:THREE.MeshStandardMaterial[]=[];
 const cutPlane=new THREE.Plane(new THREE.Vector3(0,-1,0),1.05);
 const mat=(color:string,roughness=.65,metalness=0)=>new THREE.MeshStandardMaterial({color,roughness,metalness});
 const plaster=mat('#e8e5dd'),white=mat('#faf9f5',.4),edge=mat('#d8d6d0'),steel=mat('#a4a9ab',.27,.85),black=mat('#1a2021',.25,.45),counter=mat('#222827',.24,.12),tile=mat('#c9c5bb',.65),grout=mat('#97968e'),porcelain=mat('#f7f6ed',.22),glass=new THREE.MeshStandardMaterial({color:'#b5c4c7',transparent:true,opacity:.18,roughness:.08,metalness:.1,depthWrite:false});
 const wallWhite=white.clone(),wallEdge=edge.clone(),wallBlack=black.clone();cutMaterials.push(plaster,wallWhite,wallEdge,wallBlack);
 const lightMat=new THREE.MeshStandardMaterial({color:'#fff8dc',emissive:'#fff4d3',emissiveIntensity:2});
 function box(w:number,h:number,d:number,x:number,y:number,z:number,m:THREE.Material=white,parent:THREE.Object3D=architecture,collision=false){const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);if(collision)colliders.push({x0:x-w/2,x1:x+w/2,z0:z-d/2,z1:z+d/2});return o;}
 function cylinder(r:number,h:number,x:number,y:number,z:number,m:THREE.Material,parent:THREE.Object3D=decor){const o=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,24),m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o;}
 function pipe(points:number[][],radius=.012,m:THREE.Material=steel,parent:THREE.Object3D=decor){const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p as [number,number,number])));const o=new THREE.Mesh(new THREE.TubeGeometry(curve,24,radius,8,false),m);parent.add(o);return o;}
 // Procedural wood grain: staggered planks, continuous fine grain, restrained knot detail.
 let seed=1234;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 const c=document.createElement('canvas');c.width=c.height=1024;const ctx=c.getContext('2d')!;
 for(let plank=0;plank<8;plank++){const px=plank*128; const tone=118+random()*26;ctx.fillStyle=`rgb(${tone+23},${tone+8},${tone-8})`;ctx.fillRect(px,0,128,1024);
 for(let k=0;k<190;k++){const x=px+random()*128;ctx.strokeStyle=`rgba(${random()>.45?'48,36,24':'237,222,197'},${.03+random()*.13})`;ctx.lineWidth=.3+random()*1.6;ctx.beginPath();ctx.moveTo(x,0);for(let y=0;y<=1024;y+=12)ctx.lineTo(x+Math.sin(y*.009+plank)*2+Math.sin(y*.027+k)*.55,y);ctx.stroke();}
 for(let knot=0;knot<2;knot++){const kx=px+25+random()*78,ky=random()*1024;for(let r=2;r<16;r++){ctx.strokeStyle='rgba(63,45,28,.10)';ctx.beginPath();ctx.ellipse(kx,ky,r*.8,r*5.4,0,0,Math.PI*2);ctx.stroke();}}
 ctx.fillStyle='rgba(39,30,22,.20)';ctx.fillRect(px,0,1.5,1024);const offset=(plank%3)*340;for(let y=offset;y<1024;y+=680)ctx.fillRect(px,y,128,1.5);}
 const woodBase=new THREE.CanvasTexture(c);woodBase.colorSpace=THREE.SRGBColorSpace;woodBase.wrapS=woodBase.wrapT=THREE.RepeatWrapping;woodBase.anisotropy=renderer.capabilities.getMaxAnisotropy();
 const textures:THREE.Texture[]=[woodBase];
 function floor(x0:number,z0:number,x1:number,z1:number,tiled=false,deck=false){const w=x1-x0,d=z1-z0;let material:THREE.Material;
 if(tiled){material=tile;}else{const map=woodBase.clone();map.repeat.set(w/1.65,d/2.8);textures.push(map);material=new THREE.MeshStandardMaterial({map,roughness:.74,color:deck?'#9f9690':'#e3dbd1'});}
 box(w,.12,d,(x0+x1)/2,-.06,(z0+z1)/2,material,architecture);
 if(tiled){for(let x=x0+.45;x<x1;x+=.45)box(.008,.003,d,x,.003,(z0+z1)/2,grout);for(let z=z0+.45;z<z1;z+=.45)box(w,.003,.008,(x0+x1)/2,.003,z,grout);}
 if(!deck)box(w,.08,d,(x0+x1)/2,2.73,(z0+z1)/2,plaster,ceilings);
 }
 floor(0,-3.22,3.58,0);floor(0,0,2.4,1.74);floor(-.43,-1.47,0,-.05);floor(3.58,-3.22,7.2,0);floor(2.4,0,7.2,4.6);floor(0,4.6,3.4,9.18);floor(0,9.18,3.06,13);floor(3.4,4.6,5.9,6.3,true);floor(3.4,6.3,5.9,8,true);floor(5.9,4.6,7.2,9.18);floor(3.4,8,5.9,9.18);floor(0,2.45,2.4,4.6,false,true);
 const bayShape=new THREE.Shape();bayShape.moveTo(3.58,3.22);bayShape.lineTo(4.56,4.12);bayShape.lineTo(6.38,4.12);bayShape.lineTo(7.2,3.25);bayShape.lineTo(7.2,3.22);bayShape.closePath();const bayFloor=new THREE.Mesh(new THREE.ShapeGeometry(bayShape),new THREE.MeshStandardMaterial({map:woodBase,roughness:.75}));bayFloor.rotation.x=-Math.PI/2;bayFloor.receiveShadow=true;architecture.add(bayFloor);const bayCeiling=bayFloor.clone();bayCeiling.material=plaster;bayCeiling.position.y=2.7;bayCeiling.rotation.x=Math.PI/2;bayCeiling.scale.y=-1;ceilings.add(bayCeiling);
 type Opening={a:number;b:number;bottom?:number;top?:number;window?:boolean};
 function wall(axis:'x'|'z',fixed:number,a:number,b:number,openings:Opening[]=[],external=false){const thick=external?.16:.12;let prev=a;
 function part(l:number,r:number,low=0,high=2.7){if(r-l<.001)return;const w=axis==='x'?r-l:thick,d=axis==='x'?thick:r-l,x=axis==='x'?(l+r)/2:fixed,z=axis==='x'?fixed:(l+r)/2;box(w,high-low,d,x,(high+low)/2,z,plaster,architecture,low<.3);if(low===0){box(w+.014,.15,d+.014,x,.075,z,wallWhite);}}
 for(const o of [...openings].sort((a,b)=>a.a-b.a)){part(prev,o.a);const low=o.bottom??0,high=o.top??2.12;if(low>0)part(o.a,o.b,0,low);part(o.a,o.b,high,2.7);
 // Casing aligned to opening; actual void allows walking through the wall.
 const center=(o.a+o.b)/2,width=o.b-o.a;
 for(const p of[o.a-.025,o.b+.025])box(axis==='x'?.065:thick+.05,high-low+.06,axis==='x'?thick+.05:.065,axis==='x'?p:fixed,(high+low)/2,axis==='x'?fixed:p,wallWhite);
 box(axis==='x'?width+.12:thick+.06,.065,axis==='x'?thick+.06:width+.12,axis==='x'?center:fixed,high+.025,axis==='x'?fixed:center,wallWhite);
 if(o.window) windowAt(axis,fixed,center,width,low,high);prev=o.b;}part(prev,b);}
 function windowAt(axis:'x'|'z',fixed:number,center:number,w:number,low:number,high:number){const group=new THREE.Group();group.position.set(axis==='x'?center:fixed,0,axis==='x'?fixed:center);if(axis==='z')group.rotation.y=Math.PI/2;architecture.add(group);const h=high-low;
 box(w,.06,.12,0,low,0,wallBlack,group);box(w,.05,.12,0,high,0,wallBlack,group);for(const x of[-w/2,w/2])box(.045,h,.12,x,(low+high)/2,0,wallBlack,group);box(w,.045,.12,0,low+h*.5,0,wallBlack,group);
 const pane=new THREE.MeshStandardMaterial({color:'#d4e2e7',roughness:.15,metalness:.2,emissive:'#a3bdc6',emissiveIntensity:.25});cutMaterials.push(pane);box(w-.07,h-.08,.016,0,(low+high)/2,0,pane,group);box(w+.18,.04,.25,0,low-.04,0,wallWhite,group);
 for(let i=0;i<6;i++)box(w+.04,.025,.065,0,high-.06-i*.045,-.095,wallEdge,group);box(w+.1,.075,.1,0,high+.01,-.09,wallWhite,group);
 }
 const win=(a:number,b:number):Opening=>({a,b,bottom:.82,top:2.27,window:true});
 // Walls traced from the newly supplied complete floor plan.
 wall('x',-3.22,0,3.58,[win(.72,1.82)],true);
 wall('z',0,-3.22,-1.47,[win(-2.65,-1.93)],true);wall('x',-1.47,-.43,0,[],true);wall('z',-.43,-1.47,-.05,[],true);wall('x',-.05,-.43,0,[],true);wall('z',0,-.05,1.74,[],true);
 wall('x',1.74,0,2.4,[],true);wall('z',3.58,-3.22,0);wall('x',0,2.4,7.2,[{a:2.65,b:3.5},{a:3.73,b:4.58}]);
 wall('z',2.4,0,4.6,[{a:2.8,b:3.66},win(3.88,4.48)],true);
 wall('z',7.2,-3.25,9.18,[win(1.6,3.1),{a:8.22,b:9.07}],true);
 wall('x',-4.12,4.56,6.38,[win(4.91,6.04)],true);
 // Angled bay-window walls, rotated from the same opening-aware construction.
 function diagonalWall(x0:number,z0:number,x1:number,z1:number){const start=architecture.children.length;const len=Math.hypot(x1-x0,z1-z0);const colliderStart=colliders.length;wall('x',0,0,len,[win(.2,len-.2)],true);const children=architecture.children.slice(start);const g=new THREE.Group();children.forEach(o=>g.add(o));g.rotation.y=-Math.atan2(z1-z0,x1-x0);g.position.set(x0,0,z0);architecture.add(g);colliders.splice(colliderStart);}
 diagonalWall(3.58,-3.22,4.56,-4.12);diagonalWall(6.38,-4.12,7.2,-3.25);
 wall('z',0,4.6,13,[win(6.2,7.18),win(10.02,10.81),win(11.25,12.09)],true);
 wall('x',4.6,0,5.9,[],true);wall('z',3.4,4.6,8);wall('x',6.3,3.4,5.9);wall('z',5.9,4.6,8,[{a:4.8,b:5.65},{a:7,b:7.85}]);
 wall('x',8,0,5.9,[{a:1.46,b:2.31},{a:2.68,b:3.3}]);wall('z',1,8,9.18);wall('x',8.72,0,1);
 wall('x',9.18,1,7.2,[{a:2.1,b:2.96}]);wall('z',3.06,9.18,13,[],true);wall('x',13,0,3.06,[],true);
 // Closed entry door; internal room openings stay open for continuous circulation.
 function panelDoor(x:number,z:number,w=.8,rotation=0){const g=new THREE.Group();g.position.set(x,0,z);g.rotation.y=rotation;architecture.add(g);box(w,2.08,.045,0,1.04,0,white,g);for(const y of[.38,.92,1.5,1.87])box(w-.15,.29,.017,0,y,-.033,edge,g);box(.11,.025,.055,w*.34,1,-.06,steel,g);return g;}
 panelDoor(7.14,8.65,.85,Math.PI/2); // Exterior door remains a boundary in walking mode.
 colliders.push({x0:7.02,x1:7.3,z0:8.2,z1:9.1});
 panelDoor(2.69,-.41,.78,Math.PI/2);panelDoor(3.78,-.41,.78,Math.PI/2);panelDoor(2.16,9.65,.78,Math.PI/2);
 // Kitchen: photo order when looking toward it is dishwasher, sink, range, fridge.
 function cabinet(x:number,w:number,y:number,h:number,depth:number,front=3.89){const z=front+depth/2;box(w,h,depth,x,y+h/2,z,white,decor,true);const count=w>.7?2:1;for(let i=0;i<count;i++){const dw=w/count-.025,dx=x-w/2+(i+.5)*w/count;box(dw,h-.055,.025,dx,y+h/2,front-.018,edge,decor);box(dw-.075,h-.13,.025,dx,y+h/2,front-.033,white,decor);box(.013,.17,.026,dx+(count===2?(i===0?.11:-.11):.1),y+h*.57,front-.057,steel,decor);} }
 const front=3.89;
 // Refrigerator at the deck end, as photographed.
 box(.75,1.88,.68,2.76,.94,4.22,steel,decor,true);box(.7,.49,.04,2.76,1.59,3.864,steel,decor);box(.7,1.18,.04,2.76,.725,3.858,steel,decor);box(.71,.022,.025,2.76,1.335,3.824,black,decor);box(.03,.38,.07,2.48,1.55,3.81,black,decor);box(.03,.57,.07,2.48,.96,3.80,black,decor);
 cabinet(3.24,.18,0,.87,.6);cabinet(4.59,.91,0,.87,.6);box(.96,.045,.67,4.59,.9,4.17,counter,decor);cabinet(5.79,.2,0,.87,.6);
 box(.6,.87,.59,5.37,.435,4.19,steel,decor,true);box(.59,.075,.018,5.37,.82,3.883,black,decor);box(.42,.025,.055,5.37,.78,3.857,steel,decor);
 box(.82,.045,.67,5.49,.9,4.17,counter,decor);
 // Recessed sink visual and high arch faucet.
 box(.55,.009,.35,4.6,.925,4.11,steel,decor);box(.48,.011,.28,4.6,.931,4.11,black,decor);box(.42,.012,.22,4.6,.935,4.11,mat('#686e6c',.22,.75),decor);
 pipe([[4.62,.94,4.37],[4.62,1.29,4.37],[4.62,1.36,4.26],[4.62,1.22,4.15]],.018);cylinder(.025,.13,4.78,.98,4.35,steel);
 // Range with burners, glass oven and microwave.
 box(.75,.87,.65,3.71,.435,4.18,steel,decor,true);box(.74,.045,.65,3.71,.9,4.16,black,decor);box(.63,.43,.025,3.71,.4,3.84,black,decor);box(.51,.29,.012,3.71,.41,3.822,mat('#293130',.18,.45),decor);box(.62,.028,.05,3.71,.66,3.799,steel,decor);box(.73,.21,.08,3.71,1.01,4.45,steel,decor);box(.22,.08,.015,3.71,1.035,4.399,black,decor);
 for(const x of[3.49,3.92])for(const z of[4.02,4.32]){cylinder(.09,.017,x,.939,z,black);box(.25,.024,.015,x,.957,z,black,decor);box(.015,.024,.25,x,.957,z,black,decor);}
 for(let i=0;i<4;i++){const knob=cylinder(.027,.025,3.45+i*.17,.82,3.829,black);knob.rotation.x=Math.PI/2;}
 cabinet(2.76,.8,1.96,.67,.36,4.14);cabinet(3.25,.16,1.53,1.1,.36,4.14);cabinet(3.72,.77,2.1,.53,.36,4.14);cabinet(4.48,.72,1.53,1.1,.36,4.14);cabinet(5.25,.79,1.53,1.1,.36,4.14);cabinet(5.75,.2,1.53,1.1,.36,4.14);
 box(.75,.42,.42,3.72,1.86,4.12,steel,decor);box(.62,.32,.018,3.68,1.86,3.901,black,decor);box(.49,.23,.012,3.65,1.86,3.889,mat('#303733',.22,.55),decor);box(.027,.28,.055,3.94,1.86,3.875,steel,decor);
 // Bathroom tubs, sliding screens, toilets, vanities and tiled surrounds.
 function bath(z0:number,mirrorSouth:boolean){const tubX=3.84,z=z0+.85;const gz=new THREE.Group();decor.add(gz);
 box(.78,.49,1.58,tubX,.245,z,porcelain,decor,true);box(.65,.025,1.42,tubX,.499,z,mat('#d9dfd9',.18),decor);box(.55,.018,1.28,tubX,.518,z,mat('#b8c4c1',.25),decor);
 box(.025,2.1,1.66,3.477,1.55,z,tile,decor);for(let yy=.54;yy<2.7;yy+=.5)box(.03,.009,1.65,3.46,yy,z,grout,decor);for(let zz=z0+.4;zz<z0+1.7;zz+=.4)box(.03,2.15,.008,3.46,1.58,zz,grout,decor);
 box(.02,1.55,1.5,4.235,1.31,z,glass,decor);box(.035,.045,1.62,4.24,2.1,z,steel,decor);box(.035,.035,1.62,4.24,.54,z,steel,decor);box(.025,1.58,.03,4.24,1.32,z,steel,decor);box(.05,.025,.48,4.29,1.32,z,steel,decor);
 pipe([[3.53,1.9,z0+.25],[3.72,1.94,z0+.25]],.016);const shower=cylinder(.07,.025,3.74,1.91,z0+.25,steel);shower.rotation.z=Math.PI/4;
 const back=mirrorSouth?z0+1.54:z0+.16,sign=mirrorSouth?-1:1;
 box(.38,.65,.2,4.63,.325,back,porcelain,decor);const bowl=new THREE.Mesh(new THREE.SphereGeometry(.25,24,16),porcelain);bowl.scale.set(1,.65,1.3);bowl.position.set(4.63,.36,back+sign*.28);decor.add(bowl);cylinder(.15,.3,4.63,.15,back+sign*.22,porcelain);const seat=cylinder(.255,.025,4.63,.47,back+sign*.29,porcelain);seat.scale.z=1.25;
 const vz=back+sign*.15;box(.68,.8,.45,5.35,.4,vz,white,decor,true);box(.72,.055,.5,5.35,.83,vz,porcelain,decor);box(.42,.008,.28,5.35,.864,vz,mat('#bdc9c7',.2),decor);
 pipe([[5.35,.86,back],[5.35,1.06,back],[5.35,1.05,back+sign*.14]],.015);
 const mz=mirrorSouth?z0+1.635:z0+.065;box(.79,.91,.06,5.35,1.63,mz,white,decor);box(.69,.79,.069,5.35,1.63,mz,mat('#9daeb1',.09,.88),decor);box(.65,.08,.12,5.35,2.2,mz,lightMat,decor);
 }
 bath(4.6,true);bath(6.3,false);
 // Closet faces and characteristic wall recesses from the photographs.
 function closet(x:number,z:number,width:number,rot=0){const g=new THREE.Group();g.position.set(x,0,z);g.rotation.y=rot;decor.add(g);box(width,2.7,.57,0,1.35,.26,plaster,g);for(let i=0;i<2;i++){const w=width/2-.025,xx=(i-.5)*width/2;box(w,2.12,.045,xx,1.06,-.055,white,g);box(w-.11,.86,.012,xx,1.56,-.083,edge,g);box(w-.11,.85,.012,xx,.55,-.083,edge,g);const knob=cylinder(.023,.015,xx+(i===0?.2:-.2),1,-.102,steel,g);knob.rotation.x=Math.PI/2;}}
 closet(6.21,-.58,1.45);closet(3.08,-2.13,1.6,Math.PI/2);closet(.49,8.31,.82);closet(.48,9.22,.8);
 colliders.push({x0:5.46,x1:6.97,z0:-.67,z1:-.02},{x0:3.0,x1:3.58,z0:-2.93,z1:-1.33},{x0:.08,x1:.9,z0:8.2,z1:8.72},{x0:.08,x1:.9,z0:9.12,z1:9.75});
 // Laundry niche opening off the short connecting hall.
 box(.65,.95,.64,2.99,.475,7.60,white,decor,true);box(.65,.72,.62,2.99,1.72,7.6,white,decor);box(.64,.23,.64,2.99,1.23,7.6,edge,decor);box(.5,.49,.025,2.99,1.76,7.925,edge,decor);box(.46,.44,.024,2.99,1.76,7.947,white,decor);for(let i=0;i<3;i++){const knob=cylinder(.034,.023,2.78+i*.17,1.27,7.934,steel);knob.rotation.x=Math.PI/2;}
 // Recessed lighting and bedroom ceiling fittings.
 const hemi=new THREE.HemisphereLight('#f3f7ff','#b7a391',2.15);scene.add(hemi);
 const sun=new THREE.DirectionalLight('#fff5df',2.8);sun.position.set(-3,9,-10);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-12;sun.shadow.camera.right=12;sun.shadow.camera.top=12;sun.shadow.camera.bottom=-12;sun.shadow.bias=-.0003;sun.shadow.normalBias=.035;scene.add(sun);sun.target.position.set(3,0,0);scene.add(sun.target);
 const lights:THREE.PointLight[]=[];
 function fixture(x:number,z:number,flush=false){cylinder(flush?.2:.065,flush?.05:.016,x,2.665,z,lightMat,ceilings);const l=new THREE.PointLight('#fff2d8',flush?8:5,7,2);l.position.set(x,2.48,z);scene.add(l);lights.push(l);}
 for(const x of[3.1,4.7,6.3])for(const z of[.8,2.8])fixture(x,z);for(const [x,z] of[[1.8,-1.5],[5.5,-2.3],[1.6,6.3],[1.5,11],[4.75,5.5],[4.75,7.1],[6.6,6.3],[4.6,8.5]])fixture(x,z,true);
 // Outlet plates, wall heaters, deck railing; small scale cues visible in photos.
 for(const z of[-1.9,.9,3.9,6.1,8]){box(.07,.115,.023,7.106,.28,z,white,decor);for(const yy of[.265,.295])box(.008,.018,.026,7.097,yy,z,black,decor);}
 for(const [x,z] of[[4.8,-.1],[1.4,4.69],[2.4,9.29]]){box(.75,.18,.06,x,.2,z,white,decor);box(.7,.035,.065,x,.22,z,black,decor);}
 for(let z=2.5;z<4.6;z+=.18)box(.03,.96,.03,.06,.49,z,steel,decor);box(.065,.06,2.1,.06,1,3.55,steel,decor);for(let x=.1;x<2.3;x+=.18)box(.03,.96,.03,x,.49,2.49,steel,decor);box(2.3,.06,.065,1.15,1,2.49,steel,decor);
 box(2.4,.09,2.15,1.2,2.77,3.525,plaster,ceilings);
 // Low presentation plinth is hidden in the interior view.
 const plinth=box(8.1,.22,17.8,3.4,-.26,4.5,mat('#565f60',.9),decor);plinth.castShadow=false;
 architecture.scale.set(planScale,1,planScale);decor.scale.set(planScale,1,planScale);ceilings.scale.set(planScale,1,planScale);
 scene.children.forEach(o=>{if(o instanceof THREE.Light){o.position.x*=planScale;o.position.z*=planScale;}});
 const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.09;controls.minDistance=5;controls.maxDistance=30;controls.maxPolarAngle=Math.PI*.48;controls.target.set(3.6,0,1.1);controls.enabled=false;
 let mode:Mode='walk',keys=new Set<string>(),yaw=0,pitch=0,drag=false,lastX=0,lastY=0,frame=0,disposed=false,lastRoom='living',fov=66;
 
 function orient(target:readonly number[]){camera.lookAt(target[0]*planScale,target[1],target[2]*planScale);yaw=camera.rotation.y;pitch=camera.rotation.x;}
 function setMode(next:Mode){mode=next;keys.clear();ceilings.visible=mode==='walk';controls.enabled=mode==='dollhouse';plinth.visible=mode!=='walk';for(const m of cutMaterials){m.clippingPlanes=mode==='walk'?[]:[cutPlane];m.needsUpdate=true;}
 if(mode==='dollhouse'){camera.fov=43;camera.position.set(17,20,23);camera.up.set(0,1,0);controls.target.set(3.6,0,4.4);camera.lookAt(3.6,0,4.4);controls.update();}
 else if(mode==='plan'){camera.fov=42;camera.position.set(3.6,29,4.4);camera.up.set(0,0,-1);camera.lookAt(3.6,0,4.4);}
 else{camera.up.set(0,1,0);camera.fov=fov;const r=rooms.find(r=>r.id===lastRoom)!;camera.position.set(r.pos[0]*planScale,r.pos[1],r.pos[2]*planScale);orient(r.target);}camera.updateProjectionMatrix();}
 function jump(id:string){const r=rooms.find(r=>r.id===id);if(!r)return;lastRoom=id;if(mode!=='walk')setMode('walk');camera.position.set(r.pos[0]*planScale,r.pos[1],r.pos[2]*planScale);orient(r.target);onRoom(id);}
 function canWalk(x:number,z:number){x/=planScale;z/=planScale;const margin=.16;const inside=floorRects.some(([x0,z0,x1,z1])=>x>x0+margin&&x<x1-margin&&z>z0+margin&&z<z1-margin);
 // Shared floor boundaries are passable: sampling four corners covers joined rectangles.
 const covered=[[-margin,-margin],[-margin,margin],[margin,-margin],[margin,margin]].every(([dx,dz])=>floorRects.some(([x0,z0,x1,z1])=>x+dx>=x0&&x+dx<=x1&&z+dz>=z0&&z+dz<=z1));
 const inBay=(px:number,pz:number)=>pz>=-4.12&&pz<=-3.22&&px>=3.58+(-3.22-pz)/.9*.98&&px<=7.2-(-3.25-pz)/.87*.82;const bayCovered=[[-margin,-margin],[-margin,margin],[margin,-margin],[margin,margin]].every(([dx,dz])=>inBay(x+dx,z+dz)||floorRects.some(([x0,z0,x1,z1])=>x+dx>=x0&&x+dx<=x1&&z+dz>=z0&&z+dz<=z1));
 return (inside||covered||bayCovered)&&!colliders.some(r=>x>r.x0-margin&&x<r.x1+margin&&z>r.z0-margin&&z<r.z1+margin);}
 function key(e:KeyboardEvent,down:boolean){if((e.target as HTMLElement)?.closest('input,select,textarea,[role=dialog]'))return;const k=e.key.toLowerCase();if(['w','a','s','d','arrowup','arrowdown','arrowleft','arrowright','q','e'].includes(k)){if(mode==='walk')e.preventDefault();if(down)keys.add(k);else keys.delete(k);}}
 const kd=(e:KeyboardEvent)=>key(e,true),ku=(e:KeyboardEvent)=>key(e,false),blur=()=>{keys.clear();drag=false;};window.addEventListener('keydown',kd);window.addEventListener('keyup',ku);window.addEventListener('blur',blur);
 const down=(e:PointerEvent)=>{if(mode!=='walk')return;drag=true;lastX=e.clientX;lastY=e.clientY;renderer.domElement.setPointerCapture(e.pointerId);};
 const move=(e:PointerEvent)=>{if(!drag||mode!=='walk')return;yaw-=(e.clientX-lastX)*.004;pitch=Math.max(-1.2,Math.min(1.2,pitch-(e.clientY-lastY)*.003));lastX=e.clientX;lastY=e.clientY;};
 const up=()=>{drag=false;};renderer.domElement.addEventListener('pointerdown',down);renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerup',up);renderer.domElement.addEventListener('pointercancel',up);
 const observer=new ResizeObserver(()=>{const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();});observer.observe(host);
 jump('living');setMode('walk');
 let lastTime=performance.now();let lastCheck=0;
 function animate(now:number){if(disposed)return;frame=requestAnimationFrame(animate);const dt=Math.min((now-lastTime)/1000,.05);lastTime=now;
 if(mode==='walk'){let forward=0,strafe=0;if(keys.has('w')||keys.has('arrowup'))forward++;if(keys.has('s')||keys.has('arrowdown'))forward--;if(keys.has('a'))strafe--;if(keys.has('d'))strafe++;if(keys.has('arrowleft')||keys.has('q'))yaw+=dt*1.35;if(keys.has('arrowright')||keys.has('e'))yaw-=dt*1.35;
 const length=Math.hypot(forward,strafe)||1,speed=1.7*dt/length;const dx=(-Math.sin(yaw)*forward+Math.cos(yaw)*strafe)*speed,dz=(-Math.cos(yaw)*forward-Math.sin(yaw)*strafe)*speed;
 if(canWalk(camera.position.x+dx,camera.position.z))camera.position.x+=dx;if(canWalk(camera.position.x,camera.position.z+dz))camera.position.z+=dz;camera.rotation.set(pitch,yaw,0,'YXZ');
 if(now-lastCheck>450){lastCheck=now;const r=rooms.find(r=>camera.position.x/planScale>r.bounds[0]&&camera.position.x/planScale<r.bounds[2]&&camera.position.z/planScale>r.bounds[1]&&camera.position.z/planScale<r.bounds[3]);if(r&&r.id!==lastRoom){lastRoom=r.id;onRoom(r.id);}}}else if(mode==='dollhouse')controls.update();
 renderer.render(scene,camera);}
 frame=requestAnimationFrame(animate);onReady();
 return {jump,setMode,setKey:(k:string,pressed:boolean)=>{if(pressed)keys.add(k);else keys.delete(k);},setFov:(v:number)=>{fov=v;if(mode==='walk'){camera.fov=v;camera.updateProjectionMatrix();}},getState:()=>({mode,room:lastRoom,position:camera.position.toArray(),canWalk:canWalk(camera.position.x,camera.position.z)}),dispose:()=>{disposed=true;cancelAnimationFrame(frame);observer.disconnect();controls.dispose();window.removeEventListener('keydown',kd);window.removeEventListener('keyup',ku);window.removeEventListener('blur',blur);scene.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();const ms=Array.isArray(o.material)?o.material:[o.material];ms.forEach(m=>m.dispose());}});textures.forEach(t=>t.dispose());envTarget.dispose();renderer.dispose();renderer.domElement.remove();}};
}
