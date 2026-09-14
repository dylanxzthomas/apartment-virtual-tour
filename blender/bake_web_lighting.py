import bpy,math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DEST=ROOT.parent/'public'/'models'/'refined';DEST.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4-refined.blend'))
s=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
s.cycles.device='GPU';s.cycles.samples=64;s.cycles.use_denoising=True
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='16';s.render.image_settings.exr_codec='ZIP'
# Capture actual apartment radiance for view-dependent metallic reflections.
camdata=bpy.data.cameras.new('Apartment reflection panorama');camdata.type='PANO';camdata.panorama_type='EQUIRECTANGULAR'
cam=bpy.data.objects.new('Apartment reflection panorama',camdata);s.collection.objects.link(cam);cam.location=(4.8,-2.2,1.35);cam.rotation_euler=(math.pi/2,0,0)
s.camera=cam;s.render.resolution_x=1536;s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.filepath=str(DEST/'room-reflections.exr')
bpy.ops.render.render(write_still=True);print('REFLECTION_CAPTURE_COMPLETE',flush=True)
# Apply geometry modifiers and preserve role/material distinctions before creating one lightmap atlas.
objects=[o for o in s.objects if o.type in {'MESH','CURVE','FONT'}]
roles={o.name:('ceiling' if 'ceiling' in o.name.lower() else 'exterior' if any(c.name=='Exterior' for c in o.users_collection) else 'interior') for o in objects}
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.convert(target='MESH')
objects=list(bpy.context.selected_objects);material_copies={};baked=[];others={}
for o in objects:
 world=o.matrix_world.copy();o.parent=None;o.matrix_world=world
 role=roles.get(o.name,'interior');o['web_role']=role
 old=o.data.materials[0] if o.data.materials else None
 if old is None:continue
 key=(old.name,role)
 if key not in material_copies:
  m=old.copy();m.name=old.name+' / '+role;m['web_role']=role
  p=m.node_tree.nodes.get('Principled BSDF') or next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  eligible=p is not None and p.inputs['Metallic'].default_value<.6 and p.inputs['Transmission Weight'].default_value<.1 and p.inputs['Emission Strength'].default_value<1
  m['baked_lighting']=eligible and role!='exterior';material_copies[key]=m
 m=material_copies[key];o.data.materials.clear();o.data.materials.append(m)
 if m.get('baked_lighting'):baked.append(o)
 else:others.setdefault((role,m.name),[]).append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in baked:o.select_set(True)
bpy.context.view_layer.objects.active=baked[0];bpy.ops.object.join();target=bpy.context.object;target.name='Baked apartment surfaces';target['web_role']='baked_surfaces'
if not target.data.uv_layers:target.data.uv_layers.new(name='UVMap')
target.data.uv_layers.active_index=0;target.data.uv_layers[0].name='UVMap'
atlas=target.data.uv_layers.new(name='Lightmap');target.data.uv_layers.active=atlas
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(70),island_margin=.003,area_weight=.2,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
print('LIGHTMAP_UV_COMPLETE',len(target.data.polygons),flush=True)
lightmap=bpy.data.images.new('Apartment diffuse illumination',width=3072,height=3072,float_buffer=True);lightmap.colorspace_settings.name='Linear Rec.709'
for m in target.data.materials:
 node=m.node_tree.nodes.new('ShaderNodeTexImage');node.name='LIGHTMAP_BAKE_TARGET';node.image=lightmap;m.node_tree.nodes.active=node
s.cycles.samples=256;s.render.bake.use_pass_direct=True;s.render.bake.use_pass_indirect=True;s.render.bake.use_pass_color=False;s.render.bake.use_clear=True;s.render.bake.margin=12
bpy.ops.object.bake(type='DIFFUSE',uv_layer='Lightmap')
lightmap.save_render(str(ROOT/'textures'/'diffuse-lightmap-raw.exr'),scene=s)
print('DIFFUSE_LIGHTMAP_COMPLETE',flush=True)
# Pack for export, retaining UV0 for grain and UV1 for the lighting atlas.
target.data.uv_layers.active_index=0;target.data.uv_layers[0].active_render=True
for m in target.data.materials:
 p=m.node_tree.nodes.get('Principled BSDF') or next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if p:
  for link in list(m.node_tree.links):
   if link.to_node==p and link.to_socket.name in {'Normal','Roughness'}:m.node_tree.links.remove(link)
  if 'oak vinyl' in m.name:p.inputs['Roughness'].default_value=.48
for (role,mat),batch in others.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in batch:o.select_set(True)
 bpy.context.view_layer.objects.active=batch[0]
 if len(batch)>1:bpy.ops.object.join()
 o=bpy.context.object;o.name=role+'__'+mat;o['web_role']=role
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type=='MESH':o.select_set(True)
output=DEST/'kitchen-living.glb'
bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_cameras=False,export_lights=False,export_extras=True,export_animations=False,export_yup=True)
# Keep an inspectable bake source separate from the editable artist scene.
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'kitchen-web-bake.blend'))
(DEST/'lighting.json').write_text(json.dumps({'exposure':2**s.view_settings.exposure,'lightMapIntensity':math.pi,'lightmap':'diffuse-lightmap-clean.exr','reflections':'room-reflections.exr','uvChannel':1,'samples':256,'source':'Cycles direct and indirect diffuse illumination, excluding albedo; apartment panorama for reflections'},indent=2))
print('BAKED_WEB_EXPORT_COMPLETE',output.stat().st_size,flush=True)
