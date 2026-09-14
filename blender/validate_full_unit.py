import bpy,ast,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4-daylight.blend'))
scene=bpy.context.scene
src=(ROOT/'extend_full_unit.py').read_text();tree=ast.parse(src)
rooms=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='rooms' for t in n.targets))
a=src.index('# Simplified solid-object collision');b=src.index("scene['render_stage']='Full unit:",a);exec(src[a:b].replace("/'models'/'full'","/'models'/'daylight'"))
views=json.loads((ROOT.parent/'public'/'daylight-tour'/'manifest.json').read_text())['views'];deps=bpy.context.evaluated_depsgraph_get();report=[]
for v in views:
 x,h,z=v['position'];origin=Vector((x,-z,h));hit,location,normal,index,obj,matrix=scene.ray_cast(deps,origin,Vector((0,0,-1)),distance=4)
 assert hit,f"No floor under {v['id']}"
 assert abs(location.z)<.04,f"{v['id']} stands on {obj.name} at {location.z}"
 closest=20
 for i in range(24):
  a=i*math.pi/12;hit,loc,*rest=scene.ray_cast(deps,origin,Vector((math.cos(a),math.sin(a),0)),distance=20)
  if hit:closest=min(closest,(loc-origin).length)
 assert closest>.17,f"{v['id']} viewpoint too close to geometry: {closest}"
 report.append({'id':v['id'],'floor':obj.name,'nearest_surface_m':round(closest,3)})
print('SCENE_VALIDATION',json.dumps(report),flush=True)
(ROOT/'scene-validation.json').write_text(json.dumps(report,indent=2))
