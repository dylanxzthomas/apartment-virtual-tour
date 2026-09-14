"""Daylight study: illustrative sky/neighbor massing, not a measured solar analysis."""
import bpy, math, ast, random, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4-full.blend'))
s=bpy.context.scene
COL={c.name:c for c in s.collection.children}
white=bpy.data.materials['White satin enamel — shaker cabinetry'];chrome=bpy.data.materials['Polished chrome']
for n in ast.parse((ROOT/'build_apartment.py').read_text()).body:
 if isinstance(n,ast.FunctionDef):exec(compile(ast.Module(body=[n],type_ignores=[]),'<helpers>','exec'))
# Remove prior daylight pass on repeat. Architecture stays untouched.
for o in list(COL['Exterior'].objects):bpy.data.objects.remove(o,do_unlink=True)
siding=bpy.data.materials['Neighbor gray siding — photo reference']
reveal=material('Daylight siding seam','#657478',.88)
for x in [-1.5,9.05]:
 # Keep the narrow light wells seen in the photos, open toward the rear yard.
 cube('Neighbor facade',(x,-5.95,1.9),(.12,18.5,7),siding,0,'Exterior')
 for z in [-1.55+i*.17 for i in range(42)]:cube('Horizontal siding reveal',(x+(.064 if x<4 else -.064),-5.95,z),(.009,18.5,.006),reveal,0,'Exterior')
 cap=bpy.data.materials['White semi-gloss trim'];cube('Neighbor parapet cap',(x,-5.95,5.425),(.22,18.5,.065),cap,.003,'Exterior')
ground=material('Daylight courtyard paving','#a3a399',.95)
cube('Exterior ground below apartment',(3.5,-1,-3.3),(42,52,.12),ground,0,'Exterior')
# Soft distant foliage suggested by rear-room photo 5; location/shape are illustrative.
leaf=material('Distant rear-yard foliage — illustrative','#44653c',.88)
n=leaf.node_tree.nodes;l=leaf.node_tree.links;p=n.get('Principled BSDF');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=3
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=color('#243e26');ramp.color_ramp.elements[1].color=color('#729250');l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
bark=material('Distant tree bark','#403b30',.95)
rng=random.Random(2861)
# Individual small leaf blades give the distant canopy a broken, leafy silhouette.
# One mesh per tree keeps the browser model compact.
for cx,cy,cz in [(-3.5,12,.4),(1.5,14,.9),(9,15,.5)]:
 verts=[];faces=[]
 clusters=[Vector((cx+rng.uniform(-1.8,1.8),cy+rng.uniform(-1.1,1.1),cz+rng.uniform(-.4,2.1))) for _ in range(20)]
 pipe('Distant tree trunk',[(cx,cy,-3.2),(cx+.12,cy,cz+.2),(cx+.05,cy,cz+1.6)],.085,bark,'Exterior')
 for c in clusters:pipe('Distant branch',[(cx+.08,cy,cz+.2),((cx+c.x)/2,(cy+c.y)/2,cz+.5),c],.018,bark,'Exterior')
 for j in range(2600):
  center=clusters[j%len(clusters)]+Vector((rng.gauss(0,.38),rng.gauss(0,.38),rng.gauss(0,.38)))
  axis=Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-.6,.6))).normalized()*rng.uniform(.07,.14)
  across=axis.cross(Vector((0,0,1))).normalized()*rng.uniform(.035,.065)
  i=len(verts);verts.extend([center-axis,center+across,center+axis,center-across]);faces.append((i,i+1,i+2,i+3))
 mesh=bpy.data.meshes.new('Individual distant leaves');mesh.from_pydata(verts,[],faces);mesh.materials.append(leaf)
 o=bpy.data.objects.new('Rear-yard leafy canopy — illustrative',mesh);COL['Exterior'].objects.link(o)
# Nishita sky provides a coherent direction, sky dome and radiance for every ray.
w=s.world;w.use_nodes=True;n=w.node_tree.nodes;n.clear();l=w.node_tree.links
sky=n.new('ShaderNodeTexSky');sky.sky_type='SINGLE_SCATTERING';sky.sun_elevation=math.radians(50);sky.sun_rotation=math.radians(135);sky.sun_size=math.radians(1.5);sky.sun_intensity=.5;sky.air_density=1;sky.aerosol_density=1.8;sky.ozone_density=1
bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=1.5;out=n.new('ShaderNodeOutputWorld');l.new(sky.outputs['Color'],bg.inputs['Color']);l.new(bg.outputs[0],out.inputs['Surface'])
# Architectural glazing: near-white low-roughness refraction for viewed rays;
# energy-reduced transparent shadow rays avoid noisy refractive caustic sampling.
original=bpy.data.materials['Clear window glass'];m=original.copy();m.name='Daylight architectural window glass'
n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(.98,.99,1,1);p.inputs['Roughness'].default_value=.012;p.inputs['IOR'].default_value=1.46
out=next(n for n in n if n.type=='OUTPUT_MATERIAL');path=n.new('ShaderNodeLightPath');transparent=n.new('ShaderNodeBsdfTransparent');transparent.inputs[0].default_value=(.96,.96,.96,1);mix=n.new('ShaderNodeMixShader');l.new(path.outputs['Is Shadow Ray'],mix.inputs[0]);l.new(p.outputs[0],mix.inputs[1]);l.new(transparent.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface'])
for o in s.objects:
 if o.type=='MESH' and 'glass' in o.name.lower() and ('window' in o.name.lower() or 'bay' in o.name.lower()):
  o.data.materials.clear();o.data.materials.append(m)
# Remove artificial window lights: the sky must illuminate through actual openings.
for o in list(s.objects):
 if o.type=='LIGHT' and 'daylight' in o.name.lower():bpy.data.objects.remove(o,do_unlink=True)
for o in s.objects:
 if o.type=='LIGHT':o.data.color=(1,.96,.90)
s.view_settings.exposure=-.7
s.cycles.max_bounces=12;s.cycles.diffuse_bounces=8;s.cycles.glossy_bounces=6;s.cycles.transmission_bounces=10;s.cycles.transparent_max_bounces=12
s.cycles.samples=192;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.015
s['daylight_basis']='Illustrative Nishita sun/sky, 50 degree elevation, 135 degree scene azimuth; not geolocated/date-calibrated. Existing side light wells retained. Rear-yard foliage inferred. Window shadow transparency approximates clear-glass transmission; viewed rays refract. Eight diffuse bounces. No artificial window fill lights.'
notes=bpy.data.texts.get('READ ME — reconstruction evidence');notes.write('\nDAYLIGHT STUDY\n'+s['daylight_basis']+'\n')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
s.cycles.device='GPU'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'2861-california-unit-4-daylight.blend'))
s.render.resolution_x=1120;s.render.resolution_y=840;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.cycles.samples=64
for prefix in ['01','04','08']:
 s.camera=next(o for o in s.objects if o.type=='CAMERA' and o.name.startswith(prefix+' —'));s.render.filepath=str(ROOT/'renders'/f'daylight-check-{prefix}.png');bpy.ops.render.render(write_still=True);print('DAYLIGHT_CHECK_DONE',prefix,flush=True)
