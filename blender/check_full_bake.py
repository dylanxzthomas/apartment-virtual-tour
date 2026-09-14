import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent;DEST=ROOT.parent/'public'/'models'/'daylight'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'full-web-bake.blend'))
s=bpy.context.scene
atlases={z:bpy.data.images.load(str(DEST/f'{z}-lightmap.exr')) for z in ['living','rear','front','exterior']}
for im in atlases.values():im.colorspace_settings.name='Linear Rec.709'
for m in bpy.data.materials:
 if not m.get('baked_lighting'):continue
 n=m.node_tree.nodes;l=m.node_tree.links;p=next((n for n in n if n.type=='BSDF_PRINCIPLED'),None)
 if not p:continue
 image=n.new('ShaderNodeTexImage');image.image=atlases[m['lightmap_zone']];uv=n.new('ShaderNodeUVMap');uv.uv_map='Lightmap';l.new(uv.outputs[0],image.inputs['Vector'])
 mult=n.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;l.new(image.outputs[0],mult.inputs[1])
 if p.inputs['Base Color'].is_linked:l.new(p.inputs['Base Color'].links[0].from_socket,mult.inputs[2])
 else:mult.inputs[2].default_value=p.inputs['Base Color'].default_value
 emit=n.new('ShaderNodeEmission');l.new(mult.outputs[0],emit.inputs['Color']);out=next(x for x in n if x.type=='OUTPUT_MATERIAL');l.new(emit.outputs[0],out.inputs['Surface'])
s.render.resolution_x=960;s.render.resolution_y=720;s.render.resolution_percentage=100;s.cycles.samples=40;s.cycles.device='GPU'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8'
for prefix in ['01','04','10']:
 s.camera=next(o for o in s.objects if o.type=='CAMERA' and o.name.startswith(prefix+' —'))
 s.render.filepath=str(ROOT/'renders'/f'full-bake-check-{prefix}.png');bpy.ops.render.render(write_still=True)
print('FULL_BAKE_CHECK_COMPLETE',flush=True)
