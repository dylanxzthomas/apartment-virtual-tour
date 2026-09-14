import bpy, math, random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4.blend'))
s=bpy.context.scene
rng=random.Random(286104)
# Replace the generic procedural oak with photo-guided grain, mapped separately onto each board.
wood=bpy.data.materials['Warm weathered oak planks — procedural grain'];wood.name='Weathered brown-gray oak vinyl'
n=wood.node_tree.nodes;l=wood.node_tree.links;n.clear()
out=n.new('ShaderNodeOutputMaterial');p=n.new('ShaderNodeBsdfPrincipled');l.new(p.outputs['BSDF'],out.inputs['Surface'])
p.inputs['Roughness'].default_value=.48
img=bpy.data.images.load(str(ROOT/'textures'/'weathered-oak-vinyl-albedo.png'));img.pack();img.use_fake_user=True
tex=n.new('ShaderNodeTexImage');tex.image=img;uv=n.new('ShaderNodeUVMap');uv.uv_map='UVMap';l.new(uv.outputs[0],tex.inputs['Vector']);l.new(tex.outputs['Color'],p.inputs['Base Color'])
ramp=n.new('ShaderNodeMapRange');ramp.inputs['To Min'].default_value=.35;ramp.inputs['To Max'].default_value=.62;l.new(tex.outputs['Color'],ramp.inputs['Value']);l.new(ramp.outputs['Result'],p.inputs['Roughness'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.23;bump.inputs['Distance'].default_value=.00065;l.new(tex.outputs['Color'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
for o in s.objects:
 if not o.name.startswith('Individual oak plank'):continue
 mesh=o.data;mesh.uv_layers.active.name='UVMap';uvdata=mesh.uv_layers.active.data
 xs=[v.co.x for v in mesh.vertices];ys=[v.co.y for v in mesh.vertices];xmin,xmax=min(xs),max(xs);ymin,ymax=min(ys),max(ys)
 board=rng.randrange(6);flip=rng.choice([True,False]);offset=rng.random()*.12
 for loop in mesh.loops:
  co=mesh.vertices[loop.vertex_index].co;u=(co.x-xmin)/(xmax-xmin);v=(co.y-ymin)/1.25
  if flip:v=1-v
  uvdata[loop.index].uv=((board+.018+u*.964)/6,.02+v*.86+offset)
# Better reflectance balance, including the dark quartz visible in the references.
def srgb(v):return v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4
for name,rgb,rough in [('Charcoal quartz counter',(20,24,23),.32),('Brushed stainless steel',(150,155,158),.26),('White satin enamel — shaker cabinetry',(235,235,230),.34)]:
 mat=bpy.data.materials[name];p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=tuple(srgb(v/255) for v in rgb)+(1,);p.inputs['Roughness'].default_value=rough
 if name=='Charcoal quartz counter':p.inputs['Specular IOR Level'].default_value=.22
 if name=='Brushed stainless steel':p.inputs['Anisotropic'].default_value=.45
for o in s.objects:
 if o.name.startswith('Plaster wall'):
  for modifier in list(o.modifiers):
   if modifier.type=='BEVEL':o.modifiers.remove(modifier)
 if o.name.startswith('Refrigerator handle'):
  o.data.bevel_depth=.0115
  for sp in o.data.splines:
   for bp in sp.bezier_points:bp.handle_left_type=bp.handle_right_type='AUTO'
# Turn the narrow end pieces into clean fillers, avoiding implausibly narrow handled doors.
for o in list(s.objects):
 if (o.name.startswith('Cabinet pull') or o.name.startswith('Upper cabinet pull') or o.name.startswith('Handle standoff')) and (o.location.x>5.72 or 3.2<o.location.x<3.32):
  bpy.data.objects.remove(o,do_unlink=True)
for light in bpy.data.lights:
 if light.name.startswith('Downlight'):light.energy=16
s.view_settings.exposure=-2.05
s.cycles.samples=128;s.cycles.use_denoising=True;s.cycles.device='GPU'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
# Persist the supplied images so the downloadable project is self-contained.
for i in [1,2,3,14]:
 im=bpy.data.images.load(str(ROOT.parent/'public'/'references'/f'{i:02}.png'),check_existing=True);im.name=f'REFERENCE {i:02}';im.pack();im.use_fake_user=True
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.overlay.show_overlays=False;a.spaces.active.shading.use_scene_world=True;a.spaces.active.shading.use_scene_lights=True
s['render_stage']='Kitchen/living material refinement, photo-guided floor grain; browser receives baked Cycles diffuse lighting and a scene-specific reflection panorama.'
s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100
s.render.filepath=str(ROOT/'renders'/'living-kitchen-refined.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'2861-california-unit-4-refined.blend'))
s.render.resolution_percentage=55;s.cycles.samples=48
bpy.ops.render.render(write_still=True)
print('REFINED_PREVIEW_COMPLETE',flush=True)
