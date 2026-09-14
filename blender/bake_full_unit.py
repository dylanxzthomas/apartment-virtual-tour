"""Bake three independent light atlases from the same full scene used by the rendered tour."""
import bpy,math,json,gzip
from pathlib import Path
ROOT=Path(__file__).resolve().parent;DEST=ROOT.parent/'public'/'models'/'daylight';DEST.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4-daylight.blend'))
s=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
s.cycles.device='GPU';s.cycles.samples=512;s.cycles.use_denoising=True
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='16';s.render.image_settings.exr_codec='ZIP'
# Export collision metadata from editable source before meshes are joined.
import ast
from mathutils import Vector
tree=ast.parse((ROOT/'extend_full_unit.py').read_text())
rooms=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='rooms' for t in n.targets))
colliders=[]
for o in s.objects:
 if o.type!='MESH' or not any(t in o.name.lower() for t in ['plaster wall','solid leaf','open door leaf','wardrobe side','wardrobe bypass','closet bypass','vanity cabinet','bathtub','toilet bowl','refrigerator body','range body','base cabinet carcass','dishwasher body','washer cabinet']):continue
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]
 if max(v.z for v in pts)<.12 or min(v.z for v in pts)>1.7:continue
 colliders.append({'name':o.name,'min':[min(v.x for v in pts),-max(v.y for v in pts)],'max':[max(v.x for v in pts),-min(v.y for v in pts)]})
(DEST/'collision.json').write_text(json.dumps({'rooms':rooms,'solids':colliders}))
objects=[o for o in s.objects if o.type in {'MESH','CURVE','FONT'}]
roles={o.name:('ceiling' if 'ceiling' in o.name.lower() else 'exterior' if any(c.name=='Exterior' for c in o.users_collection) else 'interior') for o in objects}
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.convert(target='MESH');objects=list(bpy.context.selected_objects)
materials={};batches={};others={}
for o in objects:
 world=o.matrix_world.copy();o.parent=None;o.matrix_world=world
 # Mesh vertex centroid matters for floor surfaces stored in global vertex coordinates.
 center=sum((o.matrix_world@v.co for v in o.data.vertices),start=__import__('mathutils').Vector())/max(1,len(o.data.vertices))
 zone='rear' if center.y>.03 else 'front' if center.y<-4.62 else 'living'
 role=roles.get(o.name,'interior');zone='exterior' if role=='exterior' else zone;o['web_role']=role;o['lightmap_zone']=zone
 old=o.data.materials[0] if o.data.materials else None
 if old is None:continue
 key=(old.name,role,zone)
 if key not in materials:
  m=old.copy();m.name=old.name+' / '+role+' / '+zone;m['web_role']=role;m['lightmap_zone']=zone
  p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  m['baked_lighting']=bool(p and p.inputs['Metallic'].default_value<.6 and p.inputs['Transmission Weight'].default_value<.1 and p.inputs['Emission Strength'].default_value<1)
  materials[key]=m
 m=materials[key];o.data.materials.clear();o.data.materials.append(m)
 (batches.setdefault(zone,[]) if m['baked_lighting'] else others.setdefault((role,m.name),[])).append(o)
targets=[]
for zone,batch in batches.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in batch:o.select_set(True)
 bpy.context.view_layer.objects.active=batch[0];bpy.ops.object.join();target=bpy.context.object;target.name='Baked '+zone;target['lightmap_zone']=zone
 if not target.data.uv_layers:target.data.uv_layers.new(name='UVMap')
 target.data.uv_layers.active_index=0;target.data.uv_layers[0].name='UVMap';atlas=target.data.uv_layers.new(name='Lightmap');target.data.uv_layers.active=atlas
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(70),island_margin=.005,margin_method='FRACTION',area_weight=.2,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
 lightmap=bpy.data.images.new(zone+' diffuse illumination',width=3072,height=3072,float_buffer=True);lightmap.colorspace_settings.name='Linear Rec.709'
 for m in target.data.materials:
  node=m.node_tree.nodes.new('ShaderNodeTexImage');node.name='LIGHTMAP_BAKE_TARGET';node.image=lightmap;m.node_tree.nodes.active=node
 s.render.bake.use_pass_direct=True;s.render.bake.use_pass_indirect=True;s.render.bake.use_pass_color=False;s.render.bake.use_clear=True;s.render.bake.margin=6;s.render.bake.margin_type='EXTEND'
 print('BAKE_START',zone,len(target.data.polygons),flush=True);bpy.ops.object.bake(type='DIFFUSE',uv_layer='Lightmap');lightmap.save_render(str(ROOT/'textures'/f'{zone}-lightmap-raw.exr'),scene=s);print('BAKE_DONE',zone,flush=True)
 target.data.uv_layers.active_index=0;target.data.uv_layers[0].active_render=True;targets.append(target)
for target in targets:
 for m in target.data.materials:
  p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if p:
   for link in list(m.node_tree.links):
    if link.to_node==p and link.to_socket.name in {'Normal','Roughness'}:m.node_tree.links.remove(link)
   if 'oak vinyl' in m.name:p.inputs['Roughness'].default_value=.48
for (role,mat),batch in others.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in batch:o.select_set(True)
 bpy.context.view_layer.objects.active=batch[0]
 if len(batch)>1:bpy.ops.object.join()
 bpy.context.object.name=role+'__'+mat
# glTF supports Principled transmission, not the Cycles shadow-ray material branch.
for m in materials.values():
 p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 out=next((n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL'),None)
 if p and out:m.node_tree.links.new(p.outputs[0],out.inputs['Surface'])
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'apartment-web.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_cameras=False,export_lights=False,export_extras=True,export_animations=False,export_yup=True)
(DEST/'apartment.glb.gz').write_bytes(gzip.compress((ROOT/'apartment-web.glb').read_bytes(),compresslevel=9,mtime=0))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'full-web-bake.blend'))
(DEST/'lighting.json').write_text(json.dumps({'zones':['living','rear','front','exterior'],'exposure':2**s.view_settings.exposure,'lightmapIntensity':math.pi,'samples':512,'source':'Daylight Cycles direct + indirect diffuse; interior and exterior lightmaps, three room reflection captures','lighting_basis':s.get('daylight_basis','')},indent=2))
print('FULL_BAKE_EXPORT_COMPLETE',flush=True)
