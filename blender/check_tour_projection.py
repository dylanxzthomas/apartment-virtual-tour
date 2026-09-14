"""Render the actual Three.js sphere/UV mapping offline to verify panorama orientation and color."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
geo=json.loads((ROOT/'tour-sphere-check.json').read_text());p=geo['positions'];verts=[(p[i],-p[i+2],p[i+1]) for i in range(0,len(p),3)];idx=geo['index'];faces=[idx[i:i+3] for i in range(0,len(idx),3)]
mesh=bpy.data.meshes.new('Web sphere');mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new(name='UVMap')
for loop in mesh.loops:uv.data[loop.index].uv=geo['uv'][loop.vertex_index*2:loop.vertex_index*2+2]
o=bpy.data.objects.new('Web panorama sphere',mesh);s.collection.objects.link(o)
mat=bpy.data.materials.new('Display ready panorama');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();image=n.new('ShaderNodeTexImage');uvnode=n.new('ShaderNodeUVMap');uvnode.uv_map='UVMap';emit=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');links=mat.node_tree.links;links.new(uvnode.outputs[0],image.inputs['Vector']);links.new(image.outputs[0],emit.inputs[0]);links.new(emit.outputs[0],out.inputs['Surface']);mesh.materials.append(mat)
cam=bpy.data.objects.new('Matched web camera',bpy.data.cameras.new('Matched web camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.sensor_width=36;cam.data.lens=36/(2*math.tan(math.radians(75)/2)*(4/3))
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
manifest=json.loads((ROOT.parent/'public'/'daylight-tour'/'manifest.json').read_text())
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['living','bed2','bed4','bath1','deck']
for id in selected:
 path=ROOT.parent/'public'/'daylight-tour'/(id+'.jpg')
 if not path.exists():continue
 view=next(v for v in manifest['views'] if v['id']==id);x,h,z=[a-b for a,b in zip(view['target'],view['position'])];cam.rotation_euler=Vector((x,-z,h)).to_track_quat('-Z','Y').to_euler()
 image.image=bpy.data.images.load(str(path));s.render.filepath=str(ROOT/'renders'/f'tour-projection-{id}.png');bpy.ops.render.render(write_still=True)
print('TOUR_PROJECTION_CHECK_COMPLETE',flush=True)
