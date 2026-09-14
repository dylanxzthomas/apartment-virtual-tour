import bpy, math, random, os, json
from mathutils import Vector
from pathlib import Path
random.seed(286104)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'renders'; OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.render.engine='CYCLES'; scene.cycles.samples=96;scene.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
scene.cycles.device='GPU'
scene.cycles.max_bounces=10;scene.cycles.diffuse_bounces=6;scene.cycles.glossy_bounces=6;scene.cycles.transmission_bounces=8
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-1.55
scene.render.film_transparent=False
scene.world.color=(.2,.2,.2)
world=scene.world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.77,.84,1,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
COL={}
for name in ['Architecture','Kitchen','Hardware','Lighting','Exterior','Cameras']:
 c=bpy.data.collections.new(name);scene.collection.children.link(c);COL[name]=c

def put(obj,group):
 for c in list(obj.users_collection):c.objects.unlink(obj)
 COL[group].objects.link(obj);return obj

def srgb(v):return v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4

def color(h):
 h=h.lstrip('#');return tuple(srgb(int(h[i:i+2],16)/255) for i in (0,2,4))+(1,)

def material(name,h,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=color(h);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color(h);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 return m
paint=material('Warm white eggshell — reference walls','#e9e7e1',.78)
white=material('White satin enamel — shaker cabinetry','#f4f3ed',.3)
trim=material('White semi-gloss trim','#f6f5f0',.27)
black=material('Black enamel and appliance glass','#101718',.18,.25)
rubber=material('Dark rubber seals','#17191a',.7)
steel=material('Brushed stainless steel','#aeb4b6',.28,.92)
chrome=material('Polished chrome','#d4d8d9',.15,1)
counter=material('Charcoal quartz counter','#252a29',.34)
inside=material('Appliance enamel interior','#d5d8d4',.31)
siding=material('Neighbor gray siding — photo reference','#7e898c',.8)
woodEdge=material('Floor seams','#655243',.8)
# Subtle surface grain and roughness on paint, steel and quartz.
for m,scale,strength,distance in [(paint,160,.14,.001),(counter,95,.13,.0012),(steel,220,.1,.0006)]:
 n=m.node_tree.nodes;l=m.node_tree.links;t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=scale;t.inputs['Detail'].default_value=2
 b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=distance;l.new(t.outputs['Fac'],b.inputs['Height']);l.new(b.outputs['Normal'],n['Principled BSDF'].inputs['Normal'])
# True volumetric refractive glass for windows and appliance fronts.
glass=material('Clear window glass','#f5faf9',.045)
glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=1
glass.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.46
ovenGlass=material('Oven glass — smoked','#283538',.12,.25)
ovenGlass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=.3
wood=bpy.data.materials.new('Warm weathered oak planks — procedural grain');wood.use_nodes=True
n=wood.node_tree.nodes;l=wood.node_tree.links;p=n['Principled BSDF'];p.inputs['Roughness'].default_value=.49
tex=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(16,1.5,3);l.new(tex.outputs['Generated'],mapping.inputs[0])
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.72;l.new(mapping.outputs[0],noise.inputs['Vector'])
wave=n.new('ShaderNodeTexWave');wave.wave_type='BANDS';wave.bands_direction='X';wave.inputs['Scale'].default_value=6;wave.inputs['Distortion'].default_value=8;wave.inputs['Detail'].default_value=5;wave.inputs['Detail Scale'].default_value=.7;l.new(mapping.outputs[0],wave.inputs['Vector'])
mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.24;l.new(noise.outputs['Fac'],mix.inputs[1]);l.new(wave.outputs['Color'],mix.inputs[2])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
for j,(pos,h) in enumerate([(0,'#504339'),(.27,'#7b6551'),(.51,'#a08b75'),(.76,'#b5a491'),(1,'#d0c0aa')]):
 e=ramp.color_ramp.elements[0] if j==0 else ramp.color_ramp.elements.new(pos);e.position=pos;e.color=tuple(v*.60 for v in color(h)[:3])+(1,)
l.new(mix.outputs[0],ramp.inputs[0])
obj=n.new('ShaderNodeObjectInfo');variation=n.new('ShaderNodeMapRange');variation.inputs['From Min'].default_value=0;variation.inputs['From Max'].default_value=1;variation.inputs['To Min'].default_value=.78;variation.inputs['To Max'].default_value=1.15;l.new(obj.outputs['Random'],variation.inputs['Value'])
tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;l.new(ramp.outputs['Color'],tint.inputs[1]);l.new(variation.outputs['Result'],tint.inputs[2]);l.new(tint.outputs[0],p.inputs['Base Color'])
b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.32;b.inputs['Distance'].default_value=.0009;l.new(mix.outputs[0],b.inputs['Height']);l.new(b.outputs['Normal'],p.inputs['Normal'])

def cube(name,loc,dim,mat=white,bevel=0,group='Kitchen'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(mat);put(o,group)
 if bevel:
  mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=bevel;mod.segments=3
  mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o

def cylinder(name,loc,r,depth,mat=chrome,rotation=None,group='Hardware'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 if rotation:o.rotation_euler=rotation
 for f in o.data.polygons:f.use_smooth=True
 mod=o.modifiers.new('Edge radius','BEVEL');mod.width=.0015;mod.segments=2
 return put(o,group)

def pipe(name,points,r=.012,mat=chrome,group='Hardware'):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=16;curve.bevel_depth=r;curve.bevel_resolution=4
 s=curve.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for bp,co in zip(s.bezier_points,points):bp.co=co;bp.handle_left_type=bp.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,curve);COL[group].objects.link(o);curve.materials.append(mat);return o

def area(name,loc,target,power,size,color_value=(1,.88,.73),size_y=None):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color_value;data.shape='RECTANGLE' if size_y else 'DISK';data.size=size
 if size_y:data.size_y=size_y
 o=bpy.data.objects.new(name,data);COL['Lighting'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

def slab_floor(x0,x1,y0,y1):
 cube('Subfloor',( (x0+x1)/2,(y0+y1)/2,-.045),(x1-x0,y1-y0,.07),woodEdge,group='Architecture')
 width=.19;length=1.25
 i=0;x=x0
 while x<x1-.001:
  w=min(width,x1-x);y=y0-((i%3)/3)*length
  while y<y1:
   a=max(y,y0);b=min(y+length,y1)
   if b>a+.005:cube('Individual oak plank', (x+w/2,(a+b)/2,-.004),(w-.0015,b-a-.0015,.017),wood,.0008,'Architecture')
   y+=length
  x+=width;i+=1
slab_floor(2.4,7.2,-4.6,0);slab_floor(5.9,7.2,-9,-4.6);slab_floor(0,7.2,0,3.5)

def wall(axis,fixed,a,b,openings=(),exterior=False):
 thick=.16 if exterior else .12
 def piece(start,end,low=0,high=2.7):
  if end-start<.001:return
  loc=((start+end)/2,fixed,(low+high)/2) if axis=='x' else (fixed,(start+end)/2,(low+high)/2)
  dim=(end-start,thick,high-low) if axis=='x' else (thick,end-start,high-low)
  cube('Plaster wall',loc,dim,paint,.004,'Architecture')
  if low==0:
   dim=(end-start,.035+thick,.155) if axis=='x' else (.035+thick,end-start,.155)
   cube('Continuous skirting', (loc[0],loc[1],.0775),dim,trim,.002,'Architecture')
 prev=a
 for lo,hi,bottom,top in sorted(openings):
  piece(prev,lo);piece(lo,hi,0,bottom) if bottom else None;piece(lo,hi,top,2.7);prev=hi
  for side in [lo-.024,hi+.024]:
   loc=(side,fixed,(bottom+top)/2) if axis=='x' else (fixed,side,(bottom+top)/2)
   dim=(.073,thick+.06,top-bottom+.04) if axis=='x' else (thick+.06,.073,top-bottom+.04)
   cube('Door / window casing',loc,dim,trim,.002,'Architecture')
  loc=((lo+hi)/2,fixed,top+.027) if axis=='x' else (fixed,(lo+hi)/2,top+.027)
  dim=(hi-lo+.12,thick+.07,.078) if axis=='x' else (thick+.07,hi-lo+.12,.078)
  cube('Casing head',loc,dim,trim,.002,'Architecture')
 piece(prev,b)
wall('x',-4.6,2.4,5.9,exterior=True)
wall('y',7.2,-9,0,[(-3.12,-1.63,.77,2.3)],True)
wall('y',2.4,-4.6,0,[(-3.88,-2.98,0,2.15),(-2.61,-1.68,.88,2.26)],True)
wall('x',0,2.4,7.2,[(2.66,3.5,0,2.14),(3.75,4.6,0,2.14)])
wall('y',5.9,-9,-4.6,[(-7.85,-7,0,2.12),(-5.65,-4.8,0,2.12)])
wall('x',-9,5.9,7.2,[(6.12,7.02,0,2.13)])
wall('y',3.58,0,3.5);wall('x',3.5,0,7.2,[(.75,2,.8,2.3),(4.4,5.6,.8,2.3)]);wall('y',0,0,3.5)
cube('Living ceiling',(4.8,-2.3,2.75),(4.8,4.6,.1),paint,.0,'Architecture');cube('Hall ceiling',(6.55,-6.8,2.75),(1.3,4.4,.1),paint,group='Architecture');cube('Rear-room ceilings',(3.6,1.75,2.75),(7.2,3.5,.1),paint,group='Architecture')

def window_xplane(name,x,y,w,bottom,top):
 h=top-bottom
 for yy in[y-w/2,y+w/2]:cube(name+' frame',(x,yy,(top+bottom)/2),(.075,.044,h),black,.002,'Architecture')
 for zz in[bottom,top,(bottom+top)/2]:cube(name+' sash',(x,y,zz),(.08,w,.048),black,.002,'Architecture')
 cube(name+' glass',(x-.015,y,(top+bottom)/2),(.007,w-.05,h-.06),glass,0,'Architecture')
 cube(name+' sill',(x,y,bottom-.035),(.29,w+.17,.052),trim,.002,'Architecture')
 # Pulled-up horizontal venetian blinds, including cords and headrail.
 inward=-1 if x>4 else 1
 for i in range(7):cube('Blind slat',(x+inward*.072,y,top-.065-i*.035),(.065,w+.06,.013),trim,.001,'Architecture')
 cube('Blind headrail',(x+inward*.07,y,top+.035),(.085,w+.10,.062),trim,.003,'Architecture')
 for yy in[y-w*.37,y+w*.37]:pipe('Blind pull cord',[(x+inward*.11,yy,top-.07),(x+inward*.11,yy,top-.36)],.0018,trim,'Architecture')
window_xplane('Living window',7.2,-2.375,1.49,.77,2.3)
window_xplane('Deck-side window',2.4,-2.145,.93,.88,2.26)
# Neighbor walls provide the restrained gray outlook visible in supplied photos.
for x in[.5,9.05]:
 cube('Neighbor facade',(x,-2.5,2.4),(.1,12,6),siding,0,'Exterior')
 for z in [.1+i*.17 for i in range(34)]:cube('Horizontal siding reveal',(x+(.061 if x<4 else -.061),-2.5,z),(.012,12,.009),rubber,0,'Exterior')
area('Window daylight',(7.04,-2.37,1.67),(3.3,-2.6,1),330,1.35,(.83,.90,1),1.25)
area('Deck daylight',(2.56,-2.13,1.7),(5,-1.8,1.2),110,.8,(.88,.94,1),1.0)
area('Rear bedroom daylight',(1.2,3.25,1.8),(2.9,-.3,.8),200,1.1,(.9,.94,1),1.3)
area('Second bedroom daylight',(5,3.25,1.8),(4.1,0,.8),170,1.1,(.9,.94,1),1.3)

def paneled_door(name,center,width=.86,angle=0):
 # Parent in local coordinates: front is +Y, vertical is Z.
 parent=bpy.data.objects.new(name,None);COL['Architecture'].objects.link(parent);before=set(bpy.data.objects)
 cube(name+' solid leaf',(0,0,1.055),(width,.043,2.11),trim,.002,'Architecture')
 for z,h in[(.36,.35),(.8,.35),(1.24,.35),(1.68,.35),(1.96,.17)]:
  cube('Recess panel',(0,.023,z),(width-.18,.008,h),white,.008,'Architecture')
  for xx in[-(width-.18)/2,(width-.18)/2]:cube('Panel moulding',(xx,.03,z),(.017,.014,h+.015),trim,.004,'Architecture')
  for zz in[z-h/2,z+h/2]:cube('Panel moulding',(0,.03,zz),(width-.16,.014,.016),trim,.004,'Architecture')
 cylinder('Latch rose',(width*.35,.05,1.02),.029,.012,steel,(math.pi/2,0,0),group='Architecture');pipe('Lever handle',[(width*.35,.06,1.02),(width*.35,.095,1.02),(width*.35-.105,.10,1.02)],.01,steel,'Architecture')
 for o in set(bpy.data.objects)-before:o.parent=parent
 parent.location=center;parent.rotation_euler.z=angle;return parent
paneled_door('Deck five-panel door',(2.38,-3.43,0),.85,-math.pi/2)
paneled_door('Unit entry door',(6.57,-8.97,0),.84)
paneled_door('Open BR2 door',(2.7,.42,0),.79,math.pi/2)
paneled_door('Open BR1 door',(3.78,.42,0),.79,math.pi/2)

# Kitchen carcasses and individually modeled shaker doors.
F=-3.92

def bar_handle(name,x,y,z,length=.17,horizontal=False):
 a=(x-length/2,y,z) if horizontal else (x,y,z-length/2)
 b=(x+length/2,y,z) if horizontal else (x,y,z+length/2)
 pipe(name,[a,b],.0055,steel)
 for pt in[a,b]:pipe('Handle standoff',[(pt[0],y-.025,pt[2]),pt],.004,steel)

def shaker(name,x,y,z,w,h):
 cube(name+' inset panel',(x,y-.005,z),(w-.07,.019,h-.075),white,.0017)
 for dx in[-w/2+.026,w/2-.026]:cube(name+' stile',(x+dx,y+.009,z),(.052,.038,h),white,.0018)
 for dz in[-h/2+.026,h/2-.026]:cube(name+' rail',(x,y+.009,z+dz),(w-.104,.038,.052),white,.0018)

def base(x,w,doors=2):
 cube('Base cabinet carcass',(x,-4.26,.48),(w,.62,.78),white,.002)
 cube('Recessed toe kick',(x,-4.31,.074),(w,.51,.12),rubber,.002)
 for i in range(doors):
  dw=w/doors-.009;dx=x-w/2+(i+.5)*w/doors;shaker('Base shaker door',dx,F,.399,dw,.615)
  bar_handle('Cabinet pull',dx+(.11 if i==0 else -.11),F+.049,.47)
 cube('Drawer front',(x,F+.011,.803),(w-.012,.04,.177),white,.002)

def upper(x,w,bottom=1.58,top=2.68,doors=2):
 h=top-bottom
 cube('Upper cabinet carcass',(x,-4.395,(bottom+top)/2),(w,.39,h),white,.002)
 for i in range(doors):
  dw=w/doors-.009;dx=x-w/2+(i+.5)*w/doors;shaker('Upper shaker door',dx,-4.185,(bottom+top)/2,dw,h-.012)
  bar_handle('Upper cabinet pull',dx+(.11 if i==0 else -.11),-4.137,bottom+.15)
 cube('Upper cornice',(x,-4.397,2.68),(w+.012,.411,.04),trim,.003)
# Spaces: fridge 2.43–3.21, narrow filler 3.22–3.31, range 3.32–4.08, sink 4.09–5.08, DW 5.09–5.7, end 5.71–5.88.
base(3.265,.09,1);base(4.59,.99,2);base(5.80,.18,1)
# Real inset sink cutout in quartz worktop.
worktop=cube('Quartz counter with sink cutout',(4.99,-4.225,.914),(1.8,.685,.035),counter,.002)
cutter=cube('Sink opening cutter',(4.57,-4.17,.9),(.55,.38,.2),rubber,.025)
mod=worktop.modifiers.new('Undermount sink opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
bpy.context.view_layer.objects.active=worktop;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
# Stainless sink basin, rounded bottom and side walls.
cube('Sink basin bottom',(4.57,-4.17,.75),(.52,.35,.025),steel,.035)
for x in[4.292,4.848]:cube('Sink basin side',(x,-4.17,.826),(.018,.36,.16),steel,.008)
for y in[-4.36,-3.98]:cube('Sink basin side',(4.57,y,.826),(.55,.018,.16),steel,.008)
cylinder('Sink drain',(4.57,-4.17,.766),.039,.005,chrome);cylinder('Drain well',(4.57,-4.17,.771),.025,.006,rubber)
for a in range(8):
 angle=a*math.pi/4;cylinder('Drain perforation',(4.57+math.cos(angle)*.018,-4.17+math.sin(angle)*.018,.775),.0025,.002,black)
pipe('Gooseneck kitchen faucet',[(4.57,-4.44,.935),(4.57,-4.44,1.27),(4.57,-4.38,1.36),(4.57,-4.24,1.35),(4.57,-4.18,1.23)],.016,chrome)
cylinder('Faucet base',(4.57,-4.44,.947),.033,.024,chrome);cylinder('Faucet side valve',(4.75,-4.43,.98),.021,.11,chrome);pipe('Faucet control',[(4.75,-4.43,1.02),(4.75,-4.40,1.13)],.007,chrome)
# Dishwasher front with fine seams and recessed control lip.
cube('Dishwasher body',(5.39,-4.25,.44),(.60,.61,.865),steel,.009)
cube('Dishwasher lower door',(5.39,-3.936,.431),(.585,.024,.727),steel,.006)
cube('Dishwasher control band',(5.39,-3.918,.821),(.585,.037,.08),black,.003)
bar_handle('Dishwasher pull',5.39,-3.89,.773,.36,True)
cube('Dishwasher plinth',(5.39,-3.982,.048),(.58,.018,.06),rubber,.003)
# Freestanding gas range with a real hollow oven cavity behind glass.
cube('Range body',(3.7,-4.255,.437),(.757,.647,.864),steel,.007)
cube('Oven dark recess',(3.7,-3.924,.408),(.639,.015,.52),black,.01)
cube('Oven glass panel',(3.7,-3.905,.404),(.558,.012,.396),ovenGlass,.025)
for z in[.30,.45,.55]:
 for x in[3.48+i*.055 for i in range(9)]:pipe('Oven rack',[(x,-4.01,z),(x,-4.40,z)],.0028,steel)
bar_handle('Oven handle',3.7,-3.856,.703,.58,True)
cube('Lower warming drawer',(3.7,-3.923,.087),(.697,.025,.10),steel,.004)
cube('Range cooktop',(3.7,-4.245,.884),(.768,.652,.045),black,.006)
for x in[3.49,3.91]:
 for y in[-4.07,-4.40]:
  cylinder('Gas burner base',(x,y,.918),.086,.018,steel);cylinder('Cast burner cap',(x,y,.933),.063,.021,black)
  for dy in[-.107,.107]:cube('Cast iron grate',(x,y+dy,.95),(.265,.012,.021),rubber,.003)
  for dx in[-.107,.107]:cube('Cast iron grate',(x+dx,y,.95),(.012,.225,.021),rubber,.003)
  for a in range(4):
   ang=a*math.pi/2;pipe('Grate spoke',[(x+math.cos(ang)*.1,y+math.sin(ang)*.1,.957),(x+math.cos(ang)*.027,y+math.sin(ang)*.027,.957)],.008,rubber)
cube('Range rear control console',(3.7,-4.52,1.035),(.755,.086,.222),steel,.01)
cube('Digital clock glass',(3.7,-4.471,1.047),(.24,.009,.075),black,.003)
blue=material('Appliance LED blue','#46aadd',.25);blue.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=color('#46aadd');blue.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=1.3
# Use a small text clock, positioned on the vertical console.
font=bpy.data.curves.new('Range time display','FONT');font.body='12:00';font.align_x='CENTER';font.size=.032;font.extrude=.0001;fo=bpy.data.objects.new('12:00 display',font);COL['Kitchen'].objects.link(fo);fo.location=(3.7,-4.464,1.031);fo.rotation_euler=(math.pi/2,0,0);font.materials.append(blue)
for x in[3.42,3.59,3.81,3.98]:
 cylinder('Range control knob',(x,-3.898,.807),.027,.036,black,(math.pi/2,0,0));cube('Knob indicator',(x,-3.875,.824),(.003,.003,.009),trim,.001)
# Refrigerator: separate bowed-look doors, rubber gaskets, caps and shaped handles.
cube('Refrigerator cabinet',(2.82,-4.215,.973),(.78,.72,1.946),steel,.018)
cube('Fridge perimeter gasket',(2.82,-3.848,.984),(.733,.013,1.87),rubber,.012)
cube('Fridge lower door',(2.82,-3.817,.655),(.722,.052,1.21),steel,.018)
cube('Freezer upper door',(2.82,-3.817,1.602),(.722,.052,.631),steel,.018)
for z,h in[(.872,.54),(1.60,.40)]:
 pipe('Refrigerator handle',[(3.088,-3.78,z-h/2),(3.088,-3.708,z-h/2+.04),(3.088,-3.697,z+h/2-.04),(3.088,-3.775,z+h/2)],.018,rubber)
for x in[2.55,3.09]:cylinder('Refrigerator leveling foot',(x,-3.97,.028),.025,.045,rubber)
upper(2.82,.82,1.99,2.68,2);upper(3.265,.095,1.58,2.68,1);upper(3.7,.772,2.115,2.68,2);upper(4.59,.99,1.58,2.68,2);upper(5.39,.605,1.58,2.68,1);upper(5.80,.18,1.58,2.68,1)
cube('Microwave stainless shell',(3.70,-4.305,1.88),(.76,.49,.447),steel,.008)
cube('Microwave glazed front',(3.69,-4.053,1.88),(.635,.012,.337),black,.004)
cube('Microwave window',(3.77,-4.042,1.89),(.42,.006,.223),ovenGlass,.006)
cube('Microwave display',(3.404,-4.043,2.00),(.086,.008,.062),black,.002)
bar_handle('Microwave vertical handle',3.459,-3.997,1.9,.29,False)
for col in range(3):
 for row in range(5):cylinder('Microwave keypad',(3.38+col*.023,-4.037,1.92-row*.026),.006,.0015,steel,(math.pi/2,0,0))
for x in[3.38+i*.028 for i in range(23)]:cube('Microwave lower vent',(x,-4.054,1.69),(.014,.004,.025),rubber,.001)
# Wall outlets and switches, faithfully sparse as in the listing images.
def outlet(x,y,z,rot=0,switch=False):
 parent=bpy.data.objects.new('Electrical faceplate',None);COL['Hardware'].objects.link(parent);before=set(bpy.data.objects)
 cube('Satin electrical plate',(0,0,0),(.073,.009,.115),trim,.003,'Hardware')
 if switch:cube('Rocker switch',(0,.008,0),(.029,.005,.055),white,.001,'Hardware')
 else:
  for zz in[-.027,.027]:
   cube('Socket inset',(0,.007,zz),(.037,.004,.036),white,.004,'Hardware')
   for xx in[-.008,.008]:cube('Socket slot',(xx,.010,zz+.004),(.003,.001,.012),black,0,'Hardware')
   cylinder('Earth pin',(0,.010,zz-.01),.003,.001,black,(math.pi/2,0,0))
 for o in set(bpy.data.objects)-before:o.parent=parent
 parent.location=(x,y,z);parent.rotation_euler.z=rot
for x in[4.20,4.94,5.70]:outlet(x,-4.506,1.17)
for y in[-.6,-3.75]:outlet(7.109,y,.30,math.pi/2)
outlet(2.49,-1.0,.29,-math.pi/2);outlet(2.49,-2.78,1.1,-math.pi/2,True)
outlet(5.0,-.071,.30,math.pi)
# Recessed ceiling trims with physically luminous discs and soft lighting.
emission=material('Warm diffused LED lens','#fff4d8',.3);ep=emission.node_tree.nodes['Principled BSDF'];ep.inputs['Emission Color'].default_value=(1,.88,.70,1);ep.inputs['Emission Strength'].default_value=5
for x in[3.2,4.75,6.3]:
 for y in[-1.05,-3.10]:
  cylinder('Recessed white trim',(x,y,2.693),.071,.011,trim,group='Lighting');cylinder('Recessed LED diffuser',(x,y,2.682),.054,.008,emission,group='Lighting')
  area('Downlight', (x,y,2.668),(x,y,0),22,.095,(1,.89,.75))
for y in[-5.55,-7.6]:
 cylinder('Hall flush lamp rim',(6.54,y,2.65),.19,.052,chrome,group='Lighting');cylinder('Hall flush diffuser',(6.54,y,2.614),.17,.028,emission,group='Lighting');area('Hall light',(6.54,y,2.59),(6.54,y,0),38,.3,(1,.90,.78))
# Approximate unseen wall heater and fire detector establish normal apartment scale.
cube('Wall heater casing',(7.10,-.9,.21),(.078,.75,.18),trim,.003,'Architecture')
for z in[.205,.235,.265]:cube('Heater vent',(7.056,-.9,z),(.008,.69,.009),rubber,.001,'Architecture')
cylinder('Smoke detector',(5.15,-.55,2.675),.057,.037,trim,group='Architecture')
# Named eye-level views tied to the supplied photos.
def camera(name,loc,target,lens=22):
 d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.05;d.clip_end=100
 o=bpy.data.objects.new(name,d);COL['Cameras'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
cam=camera('01 — living toward kitchen (photo 1)',(6.80,-.38,1.58),(3.88,-3.84,1.18),22)
camera('02 — kitchen elevation (photo 2)',(4.72,-.54,1.47),(4.11,-4.32,1.33),24)
camera('03 — toward bedrooms (photo 3)',(6.60,-4.10,1.58),(3.85,-.12,1.17),21)
scene.camera=cam
scene['reference_basis']='Apartment 4, 2861 California. User-supplied photos 1–12 and full plan. Approximate dimensions; unseen details inferred with permission.'
scene['render_stage']='Kitchen / living detailed scene. Remaining unit retains the separate browser layout prototype.'
# Store the source photos inside the blend for review, without altering them.
for i in [1,2,3,14]:
 img=bpy.data.images.load(str(ROOT.parent/'public'/'references'/f'{i:02}.png'),check_existing=True);img.name=f'REFERENCE {i:02}';img.pack()
# Open to a useful camera-aligned material preview rather than an arbitrary default view.
for screen in bpy.data.screens:
 for area_ui in screen.areas:
  if area_ui.type=='VIEW_3D':
   area_ui.spaces.active.region_3d.view_perspective='CAMERA';area_ui.spaces.active.shading.type='MATERIAL'
scene.render.filepath=str(OUT/'living-kitchen-preview.png')
# Initial preview is lower resolution; final render settings are retained in saved .blend.
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'2861-california-unit-4.blend'))
scene.render.resolution_percentage=60;scene.cycles.samples=40
bpy.ops.render.render(write_still=True)
print('APARTMENT_RENDER_COMPLETE',scene.render.filepath)
