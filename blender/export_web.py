import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4.blend'))
s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8
s.render.threads_mode='FIXED';s.render.threads=6
wood=bpy.data.materials['Warm weathered oak planks — procedural grain']
plank=next(o for o in s.objects if o.name.startswith('Individual oak plank') and o.dimensions.y>1.2)
bpy.ops.object.select_all(action='DESELECT');plank.select_set(True);bpy.context.view_layer.objects.active=plank
image=bpy.data.images.new('Baked oak base color',width=1024,height=1024)
node=wood.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;wood.node_tree.nodes.active=node
s.render.bake.use_pass_direct=False;s.render.bake.use_pass_indirect=False;s.render.bake.use_pass_color=True;s.render.bake.margin=12
bpy.ops.object.bake(type='DIFFUSE')
p=wood.node_tree.nodes.get('Principled BSDF')
for link in list(wood.node_tree.links):
 if link.to_node==p and link.to_socket.name in ['Base Color','Normal']:wood.node_tree.links.remove(link)
wood.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
# Baked color replaces Blender-only procedural nodes; the source .blend is untouched.
for m in bpy.data.materials:
 if not m.use_nodes:continue
 for link in list(m.node_tree.links):
  if link.to_node.type=='BSDF_PRINCIPLED' and link.to_socket.name=='Normal':m.node_tree.links.remove(link)
# Evaluate manufacturing bevels and convert curves, then batch by material and role.
objects=[o for o in s.objects if o.type in {'MESH','CURVE'}]
roles={o.name:('ceiling' if 'ceiling' in o.name.lower() else ('exterior' if any(c.name=='Exterior' for c in o.users_collection) else 'interior')) for o in objects}
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.convert(target='MESH')
objects=list(bpy.context.selected_objects)
for o in objects:
 world=o.matrix_world.copy();o.parent=None;o.matrix_world=world
batches={}
for o in objects:
 role=roles.get(o.name,'interior');mat=o.data.materials[0].name if o.data.materials else 'none'
 batches.setdefault((role,mat),[]).append(o)
for (role,mat),batch in batches.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in batch:o.select_set(True)
 bpy.context.view_layer.objects.active=batch[0];bpy.ops.object.join()
 o=bpy.context.object;o.name=role+'__'+mat;o['web_role']=role
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type=='MESH':o.select_set(True)
output=ROOT.parent/'public'/'models'/'kitchen-living.glb'
bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_extras=True,export_animations=False,export_yup=True)
print('WEB_EXPORT_COMPLETE',output,output.stat().st_size)
