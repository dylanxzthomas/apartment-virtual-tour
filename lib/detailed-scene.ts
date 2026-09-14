import * as THREE from 'three';
import {roomViewpoints} from './viewpoints';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { EXRLoader } from 'three/examples/jsm/loaders/EXRLoader.js';
import {rooms,type Mode} from './apartment-data';
import {inPolygon,canWalkAt,type CollisionData} from './navigation';

// This is the actual exported Blender geometry. glTF converts Blender Z-up to Y-up.
export function createDetailedApartment(host:HTMLDivElement,onRoom:(id:string)=>void,onReady:()=>void,onError:(message:string)=>void){
 const scene=new THREE.Scene();scene.background=new THREE.Color('#cbd4d8');let exposure=2**-.7;
 const camera=new THREE.PerspectiveCamera(60,1,.04,80);camera.rotation.order='YXZ';
 const renderer=new THREE.WebGLRenderer({antialias:true});
 renderer.setPixelRatio(Math.min(devicePixelRatio,1.8));renderer.toneMapping=THREE.AgXToneMapping;
 renderer.toneMappingExposure=exposure;renderer.localClippingEnabled=true;
 renderer.domElement.tabIndex=0;renderer.domElement.setAttribute('aria-label','Detailed apartment with baked lighting. Drag to look, W A S D to walk.');host.appendChild(renderer.domElement);
 // Diffuse lighting comes from Cycles. The room panorama supplies only the changing reflections.
 const pmrem=new THREE.PMREMGenerator(renderer);const envTargets:Record<string,THREE.WebGLRenderTarget>={},lightmaps:Record<string,THREE.DataTexture>={};let collision:CollisionData|undefined,currentRoom='living',pendingRoom='living',currentZone='living';
 scene.environmentIntensity=1;scene.environmentRotation.y=-Math.PI/2;
 const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.enabled=false;controls.minDistance=3;controls.maxDistance=35;controls.maxPolarAngle=Math.PI*.48;
 let model:THREE.Group|undefined,mode:Mode='walk',yaw=0,pitch=0,fov=60,disposed=false,loaded=false,frame=0,drag=false,lastX=0,lastY=0;
 const velocity=new THREE.Vector2();
 const keys=new Set<string>(),materials=new Set<THREE.MeshStandardMaterial>();
 const clipping=new THREE.Plane(new THREE.Vector3(0,-1,0),1.1);
 const release=(root:THREE.Object3D)=>{const textures=new Set<THREE.Texture>(),mats=new Set<THREE.Material>();root.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])mats.add(m);}});for(const m of mats){for(const value of Object.values(m))if(value instanceof THREE.Texture)textures.add(value);m.dispose();}textures.forEach(t=>t.dispose());};
 function setMode(next:Mode){mode=next;renderer.toneMappingExposure=exposure;keys.clear();velocity.set(0,0);controls.enabled=next==='dollhouse';
  materials.forEach(m=>{m.visible=next==='walk'||!['ceiling','exterior'].includes(m.userData.web_role);m.clippingPlanes=next==='walk'?[]:[clipping];m.needsUpdate=true;});
  camera.up.set(0,1,0);
  if(next==='walk'){camera.fov=fov;camera.position.set(6.8,1.58,.38);camera.lookAt(3.88,1.18,3.84);yaw=camera.rotation.y;pitch=camera.rotation.x;}
  else if(next==='dollhouse'){camera.fov=44;camera.position.set(18,19,23);controls.target.set(3.6,0,4.4);camera.lookAt(controls.target);controls.update();}
  else{camera.fov=43;camera.position.set(3.6,26,4.4);camera.up.set(0,0,-1);camera.lookAt(3.6,0,4.4);}
  camera.updateProjectionMatrix();
 }
 function canWalk(x:number,z:number){return !!collision&&canWalkAt(collision,x,z);}
 function setEnvironment(){const zone=camera.position.z<0?'rear':camera.position.z>4.6?'front':'living';if(envTargets[zone])scene.environment=envTargets[zone].texture;currentZone=zone;renderer.toneMappingExposure=exposure;}
 function jump(id:string){pendingRoom=id;if(!loaded)return;const r=rooms.find(r=>r.id===id)||rooms[0];setMode('walk');const view=roomViewpoints[r.id];camera.position.set(...view.position);camera.lookAt(...view.target);yaw=camera.rotation.y;pitch=camera.rotation.x;currentRoom=r.id;setEnvironment();onRoom(r.id);}
 const onKey=(e:KeyboardEvent,down:boolean)=>{if((e.target as HTMLElement)?.closest('input,select,textarea,[role=dialog]'))return;const key=e.key.toLowerCase();if(['w','a','s','d','arrowup','arrowdown','arrowleft','arrowright','q','e'].includes(key)){if(mode==='walk')e.preventDefault();if(down)keys.add(key);else keys.delete(key);}};
 const kd=(e:KeyboardEvent)=>onKey(e,true),ku=(e:KeyboardEvent)=>onKey(e,false),blur=()=>{keys.clear();drag=false;};
 window.addEventListener('keydown',kd);window.addEventListener('keyup',ku);window.addEventListener('blur',blur);
 const down=(e:PointerEvent)=>{if(mode!=='walk')return;drag=true;lastX=e.clientX;lastY=e.clientY;renderer.domElement.setPointerCapture(e.pointerId);};
 const move=(e:PointerEvent)=>{if(!drag||mode!=='walk')return;yaw-=(e.clientX-lastX)*.004;pitch=THREE.MathUtils.clamp(pitch-(e.clientY-lastY)*.003,-1.2,1.2);lastX=e.clientX;lastY=e.clientY;};
 const up=()=>{drag=false;};
 renderer.domElement.addEventListener('pointerdown',down);renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerup',up);renderer.domElement.addEventListener('pointercancel',up);
 const resize=()=>{const w=Math.max(host.clientWidth,1),h=Math.max(host.clientHeight,1);renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();};
 const observer=new ResizeObserver(resize);observer.observe(host);resize();setMode('walk');
 const loader=new EXRLoader();
 const zones=['living','rear','front'];const atlasZones=[...zones,'exterior'];
 Promise.allSettled([
  fetch('/models/daylight/apartment.glb.gz').then(async r=>{if(!r.ok)throw new Error('Missing compressed model');const packed=await r.arrayBuffer(),magic=new Uint8Array(packed,0,2);const data=magic[0]===31&&magic[1]===139?await new Response(new Blob([packed]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer():packed;return new GLTFLoader().parseAsync(data,'');}),
  ...atlasZones.map(z=>loader.loadAsync(`/models/daylight/${z}-lightmap.exr`)),
  ...zones.map(z=>loader.loadAsync(`/models/daylight/${z}-reflections.exr`)),
  fetch('/models/daylight/collision.json').then(r=>{if(!r.ok)throw new Error('Missing collision model');return r.json();}),
  fetch('/models/daylight/lighting.json').then(r=>{if(!r.ok)throw new Error('Missing lighting settings');return r.json();}),
 ]).then(results=>{
  if(disposed||results.some(r=>r.status==='rejected')){
   for(const [i,r] of results.entries())if(r.status==='fulfilled'){if(i===0)release((r.value as {scene:THREE.Group}).scene);else if(r.value instanceof THREE.Texture)r.value.dispose();}
   if(!disposed)onError('The free-walk model could not finish loading. Switch to Rendered tour or reload.');return;
  }
  const values=results.map(r=>(r as PromiseFulfilledResult<unknown>).value);
  model=(values[0] as {scene:THREE.Group}).scene;collision=values[8] as CollisionData;const lighting=values[9] as {exposure:number};if(!Number.isFinite(lighting.exposure)||lighting.exposure<=0)throw new Error('Invalid lighting exposure');exposure=lighting.exposure;
  for(let i=0;i<4;i++){
   const map=values[1+i] as THREE.DataTexture;map.channel=1;map.repeat.set(1,-1);map.offset.set(0,1);map.colorSpace=THREE.LinearSRGBColorSpace;lightmaps[atlasZones[i]]=map;
  }
  for(let i=0;i<3;i++){
   const pano=values[5+i] as THREE.DataTexture;pano.mapping=THREE.EquirectangularReflectionMapping;envTargets[zones[i]]=pmrem.fromEquirectangular(pano);pano.dispose();
  }
  pmrem.dispose();scene.environment=envTargets.living.texture;
  model.traverse(o=>{if(o instanceof THREE.Mesh)for(const mat of Array.isArray(o.material)?o.material:[o.material])if(mat instanceof THREE.MeshStandardMaterial){
   materials.add(mat);if(mat.map)mat.map.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
   if(mat.userData.baked_lighting){
    if(!o.geometry.getAttribute('uv1'))throw new Error('Baked mesh is missing its second UV channel');
    mat.lightMap=lightmaps[mat.userData.lightmap_zone];mat.lightMapIntensity=Math.PI;
    mat.onBeforeCompile=shader=>{shader.fragmentShader=shader.fragmentShader.replace('#include <lights_fragment_maps>',THREE.ShaderChunk.lights_fragment_maps.replace('iblIrradiance += getIBLIrradiance( geometryNormal );','// Diffuse irradiance is already included in the Cycles atlas.'));};
    mat.customProgramCacheKey=()=> 'cycles-diffuse-atlas-v2';
   }
   if(mat.name.includes('oak vinyl')&&mat.map){mat.bumpMap=mat.map.clone();mat.bumpMap.colorSpace=THREE.NoColorSpace;mat.bumpScale=.00065;mat.roughnessMap=mat.bumpMap;mat.roughness=.83;}
   if(mat instanceof THREE.MeshPhysicalMaterial&&mat.transmission>0){mat.transmission=0;mat.transparent=true;mat.opacity=.12;mat.depthWrite=false;}
  }});
  scene.add(model);loaded=true;jump(pendingRoom);onReady();
 }).catch(error=>{if(!disposed){console.error(error);onError('The free-walk view could not initialize. Switch to Rendered tour.');}});
 let lastTime=performance.now();
 function animate(now:number){if(disposed)return;frame=requestAnimationFrame(animate);const dt=Math.min((now-lastTime)/1000,.05);lastTime=now;
  if(mode==='walk'&&loaded){let forward=Number(keys.has('w')||keys.has('arrowup'))-Number(keys.has('s')||keys.has('arrowdown')),side=Number(keys.has('d'))-Number(keys.has('a'));
   if(keys.has('arrowleft')||keys.has('q'))yaw+=dt*1.35;if(keys.has('arrowright')||keys.has('e'))yaw-=dt*1.35;
   const speed=1.6/(Math.hypot(forward,side)||1),ease=1-Math.exp(-dt*12);
   velocity.x=THREE.MathUtils.lerp(velocity.x,(-Math.sin(yaw)*forward+Math.cos(yaw)*side)*speed,ease);velocity.y=THREE.MathUtils.lerp(velocity.y,(-Math.cos(yaw)*forward-Math.sin(yaw)*side)*speed,ease);
   const dx=velocity.x*dt,dz=velocity.y*dt;
   if(canWalk(camera.position.x+dx,camera.position.z))camera.position.x+=dx;if(canWalk(camera.position.x,camera.position.z+dz))camera.position.z+=dz;camera.rotation.set(pitch,yaw,0,'YXZ');
   const r=rooms.find(r=>inPolygon(camera.position.x,camera.position.z,r.polygon));if(r&&r.id!==currentRoom){currentRoom=r.id;renderer.toneMappingExposure=exposure;onRoom(r.id);}
   const zone=camera.position.z<0?'rear':camera.position.z>4.6?'front':'living';if(zone!==currentZone)setEnvironment();
  }else if(mode==='dollhouse')controls.update();renderer.render(scene,camera);
 }
 frame=requestAnimationFrame(animate);
 return {jump,setMode,setKey:(key:string,pressed:boolean)=>{if(pressed)keys.add(key);else keys.delete(key);},setFov:(value:number)=>{fov=value;if(mode==='walk'){camera.fov=fov;camera.updateProjectionMatrix();}},getState:()=>({mode,room:currentRoom,position:camera.position.toArray(),canWalk:canWalk(camera.position.x,camera.position.z)}),dispose:()=>{disposed=true;cancelAnimationFrame(frame);observer.disconnect();controls.dispose();window.removeEventListener('keydown',kd);window.removeEventListener('keyup',ku);window.removeEventListener('blur',blur);if(model)release(model);Object.values(lightmaps).forEach(t=>t.dispose());Object.values(envTargets).forEach(t=>t.dispose());pmrem.dispose();renderer.dispose();renderer.domElement.remove();}};
}
