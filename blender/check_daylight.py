"""Read-only daylight aperture/sky visibility audit of the delivered Blender scene."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4-daylight.blend'))
s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();windows=[]
for o in s.objects:
 if o.type!='MESH' or not any(m and m.name=='Daylight architectural window glass' for m in o.data.materials):continue
 verts=[v.co for v in o.data.vertices];dims=[max(v[a] for v in verts)-min(v[a] for v in verts) for a in range(3)];axis=min(range(3),key=lambda a:dims[a]);v=Vector((0,0,0));v[axis]=1;n=(o.matrix_world.to_3x3()@v).normalized();center=o.matrix_world@(sum(verts,Vector())/len(verts))
 if n.dot(center-Vector((3.6,-4,1.55)))<0:n=-n
 start=center+n*.16;open_sky=0;total=0
 for elevation in [20,35,50,65,80]:
  for offset in [-50,-25,0,25,50]:
   az=math.atan2(n.y,n.x)+math.radians(offset);e=math.radians(elevation);direction=Vector((math.cos(az)*math.cos(e),math.sin(az)*math.cos(e),math.sin(e)))
   hit,*_=s.ray_cast(deps,start,direction,distance=200);total+=1;open_sky+=not hit
 windows.append({'window':o.name,'unblocked_sky_directions':open_sky,'sampled_directions':total})
assert len(windows)==10,windows
# Rear-facing apertures must have an open sky path; close side facades may block lower angles.
assert all(w['unblocked_sky_directions']>0 for w in windows if 'rear' in w['window'].lower())
report={'sky_model':'SINGLE_SCATTERING','world_strength':1.5,'exposure_ev':s.view_settings.exposure,'diffuse_bounces':s.cycles.diffuse_bounces,'window_apertures':windows,'note':'Discrete geometric sky-visibility check, not illuminance or a measured daylight factor.'}
(ROOT/'daylight-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
