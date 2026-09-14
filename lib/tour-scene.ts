import * as THREE from 'three';
import type {Mode} from './apartment-data';
type View={id:string;room:string;name:string;position:number[];target:number[];links:string[]};
type Manifest={views:View[];anchors:Record<string,number[]>};
export function createRenderedTour(host:HTMLDivElement,onRoom:(id:string)=>void,onReady:()=>void,onError:(message:string)=>void){
 const scene=new THREE.Scene();scene.background=new THREE.Color('#101518');
 const camera=new THREE.PerspectiveCamera(65,1,.05,100);camera.rotation.order='YXZ';
 const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.NoToneMapping;
 renderer.domElement.tabIndex=0;renderer.domElement.setAttribute('aria-label','Blender rendered 360 degree tour. Drag to look, scroll to zoom, click a room marker to move.');host.appendChild(renderer.domElement);
 const geometry=new THREE.SphereGeometry(20,64,32);geometry.scale(-1,1,1);
 const material=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true});const sphere=new THREE.Mesh(geometry,material);
 // Blender equirectangular camera looks down -plan-Z at image center; align the sphere to world axes.
 sphere.rotation.y=-Math.PI/2;scene.add(sphere);
 const overlay=document.createElement('div');overlay.className='tour-hotspots';host.appendChild(overlay);
 const status=document.createElement('div');status.className='tour-status';status.setAttribute('role','status');host.appendChild(status);
 let manifest:Manifest|undefined,current:View|undefined,disposed=false,frame=0,drag=false,lastX=0,lastY=0,yaw=0,pitch=0,request=0,pendingRoom='living',currentTexture:THREE.Texture|undefined;
 let pins:{button:HTMLButtonElement;direction:THREE.Vector3}[]=[];
 const keys=new Set<string>();const textureLoader=new THREE.TextureLoader();
 const defaultView=(id:string)=>manifest?.views.find(v=>v.id===id)||manifest?.views.find(v=>v.room===id);
 async function jump(id:string){pendingRoom=id;if(!manifest)return;const view=defaultView(id);if(!view)return;const token=++request;status.textContent='Rendering already complete · loading viewpoint…';status.hidden=false;
  try{const tex=await textureLoader.loadAsync(`/daylight-tour/${view.id}.jpg`);if(disposed||token!==request){tex.dispose();return;}
   tex.colorSpace=THREE.SRGBColorSpace;tex.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
   currentTexture?.dispose();currentTexture=tex;material.map=tex;material.needsUpdate=true;material.opacity=window.matchMedia('(prefers-reduced-motion: reduce)').matches?1:0;
   current=view;camera.position.set(0,0,0);camera.lookAt(new THREE.Vector3(...view.target as [number,number,number]).sub(new THREE.Vector3(...view.position as [number,number,number])));yaw=camera.rotation.y;pitch=camera.rotation.x;
   overlay.replaceChildren();pins=[];
   for(const next of view.links){const dest=defaultView(next);if(!dest)continue;const anchor=manifest!.anchors[view.id+':'+next]||dest.position;
    const direction=new THREE.Vector3(...anchor as [number,number,number]).sub(new THREE.Vector3(...view.position as [number,number,number])).normalize().multiplyScalar(8);
    const button=document.createElement('button');button.className='tour-hotspot';button.type='button';button.textContent='↗ '+dest.name;button.setAttribute('aria-label','Move to '+dest.name);button.onclick=()=>void jump(next);overlay.appendChild(button);pins.push({button,direction});
   }
   status.hidden=true;onRoom(view.room);onReady();
  }catch{if(!disposed&&token===request){status.hidden=true;onError('This rendered viewpoint could not load. Select another room or switch to Free walk.');}}
 }
 fetch('/daylight-tour/manifest.json').then(r=>{if(!r.ok)throw new Error('Manifest unavailable');return r.json() as Promise<Manifest>;}).then((m:Manifest)=>{if(disposed)return;manifest=m;void jump(pendingRoom);}).catch(()=>{if(!disposed)onError('The rendered tour could not load. Switch to Free walk or reload.');});
 const resize=()=>{const w=Math.max(1,host.clientWidth),h=Math.max(1,host.clientHeight);renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();};const observer=new ResizeObserver(resize);observer.observe(host);resize();
 const down=(e:PointerEvent)=>{renderer.domElement.focus({preventScroll:true});drag=true;lastX=e.clientX;lastY=e.clientY;renderer.domElement.setPointerCapture(e.pointerId);};
 const move=(e:PointerEvent)=>{if(!drag)return;yaw-=(e.clientX-lastX)*.0035;pitch=THREE.MathUtils.clamp(pitch-(e.clientY-lastY)*.003,-1.4,1.4);lastX=e.clientX;lastY=e.clientY;};const up=()=>{drag=false;};
 const wheel=(e:WheelEvent)=>{e.preventDefault();camera.fov=THREE.MathUtils.clamp(camera.fov+e.deltaY*.035,40,85);camera.updateProjectionMatrix();};
 const key=(e:KeyboardEvent,pressed:boolean)=>{if((e.target as HTMLElement)?.closest('button,input,textarea,select,[role=dialog]'))return;if(e.key.startsWith('Arrow')){e.preventDefault();pressed?keys.add(e.key.toLowerCase()):keys.delete(e.key.toLowerCase());}};const kd=(e:KeyboardEvent)=>key(e,true),ku=(e:KeyboardEvent)=>key(e,false),blur=()=>{keys.clear();drag=false;};
 renderer.domElement.addEventListener('pointerdown',down);renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerup',up);renderer.domElement.addEventListener('pointercancel',up);renderer.domElement.addEventListener('wheel',wheel,{passive:false});window.addEventListener('keydown',kd);window.addEventListener('keyup',ku);window.addEventListener('blur',blur);
 let last=performance.now();function animate(now:number){if(disposed)return;frame=requestAnimationFrame(animate);const dt=Math.min((now-last)/1000,.05);last=now;
 yaw+=(Number(keys.has('arrowleft'))-Number(keys.has('arrowright')))*dt;pitch=THREE.MathUtils.clamp(pitch+(Number(keys.has('arrowup'))-Number(keys.has('arrowdown')))*dt,-1.4,1.4);camera.rotation.set(pitch,yaw,0,'YXZ');camera.updateMatrixWorld();material.opacity=Math.min(1,material.opacity+dt*3);
 const forward=new THREE.Vector3();camera.getWorldDirection(forward);for(const pin of pins){const visible=pin.direction.dot(forward)>0;const p=pin.direction.clone().project(camera);pin.button.hidden=!visible||Math.abs(p.x)>.92||Math.abs(p.y)>.83;pin.button.style.left=`${(p.x*.5+.5)*100}%`;pin.button.style.top=`${(-p.y*.5+.5)*100}%`;}
 renderer.render(scene,camera);
 }frame=requestAnimationFrame(animate);
 return {jump:(id:string)=>{void jump(id);},setMode:(_m:Mode)=>{},setKey:(key:string,pressed:boolean)=>{pressed?keys.add(key):keys.delete(key);},setFov:(fov:number)=>{camera.fov=THREE.MathUtils.clamp(fov,40,85);camera.updateProjectionMatrix();},getState:()=>({mode:'walk' as Mode,room:current?.room||'living',position:(current?.position||[0,0,0]) as [number,number,number],canWalk:false}),dispose:()=>{disposed=true;++request;cancelAnimationFrame(frame);observer.disconnect();window.removeEventListener('keydown',kd);window.removeEventListener('keyup',ku);window.removeEventListener('blur',blur);geometry.dispose();material.dispose();currentTexture?.dispose();renderer.dispose();renderer.domElement.remove();overlay.remove();status.remove();}};
}
