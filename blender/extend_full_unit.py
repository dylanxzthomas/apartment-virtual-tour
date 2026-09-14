"""Extend the photo-matched kitchen into the full supplied plan; units are estimated metres.
Blender coordinates (x, -plan_z, height). No claim of measured photogrammetry.
"""
import bpy, math, random, ast, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4-refined.blend'))
scene=bpy.context.scene
COL={c.name:c for c in scene.collection.children}
paint=bpy.data.materials['Warm white eggshell — reference walls'];white=bpy.data.materials['White satin enamel — shaker cabinetry'];trim=bpy.data.materials['White semi-gloss trim'];black=bpy.data.materials['Black enamel and appliance glass'];rubber=bpy.data.materials['Dark rubber seals'];steel=bpy.data.materials['Brushed stainless steel'];chrome=bpy.data.materials['Polished chrome'];glass=bpy.data.materials['Clear window glass'];wood=bpy.data.materials['Weathered brown-gray oak vinyl'];woodEdge=bpy.data.materials['Floor seams'];emission=bpy.data.materials['Warm diffused LED lens'];siding=bpy.data.materials['Neighbor gray siding — photo reference']
# Reuse construction helpers without running the old kitchen-only generator.
tree=ast.parse((ROOT/'build_apartment.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),'<helpers>','exec'))

for group in ['Architecture','Exterior']:
 for o in list(COL[group].objects):bpy.data.objects.remove(o,do_unlink=True)
for o in list(COL['Lighting'].objects):
 if any(t in o.name for t in ['Rear bedroom','Second bedroom']):bpy.data.objects.remove(o,do_unlink=True)
for name in ['Bedrooms','Bathrooms','Laundry','Deck']:
 c=bpy.data.collections.new(name);scene.collection.children.link(c);COL[name]=c
ceramic=material('Glazed white porcelain','#f4f3ef',.19)
tile=material('Warm gray porcelain wall tile','#aca79e',.48)
floorTile=material('Ivory bathroom floor tile','#d4d1c8',.55)
grout=material('Fine warm gray grout','#827e76',.85)
mirror=material('Silver mirror','#f5f7f7',.025,1)
deckmat=material('Covered deck painted boards — inferred','#95928b',.8)
rng=random.Random(286104)
# Lower detail far exterior only, to give windows restrained real light and a neighboring facade.
for x in [-1.5,9.05]:
 cube('Neighbor facade',(x,-4,2.4),(.1,24,7),siding,0,'Exterior')
 for z in [i*.17 for i in range(36)]:cube('Horizontal siding reveal',(x+(.061 if x<4 else -.061),-4,z),(.012,24,.007),rubber,0,'Exterior')
# Every wall aperture is modeled as an actual opening, including the angled rear bay.
def wall(axis,fixed,a,b,openings=(),exterior=False):
 thick=.16 if exterior else .12
 def box(st,en,lo,hi):
  if en-st<.001 or hi-lo<.001:return
  loc=((st+en)/2,fixed,(lo+hi)/2) if axis=='x' else (fixed,(st+en)/2,(lo+hi)/2)
  dim=(en-st,thick,hi-lo) if axis=='x' else (thick,en-st,hi-lo)
  cube('Plaster wall',loc,dim,paint,0,'Architecture')
  if lo==0:
   dim=(en-st,thick+.032,.155) if axis=='x' else (thick+.032,en-st,.155)
   cube('Continuous skirting',(loc[0],loc[1],.0775),dim,trim,.001,'Architecture')
 prev=a
 for lo,hi,bottom,top in sorted(openings):
  box(prev,lo,0,2.7);box(lo,hi,0,bottom);box(lo,hi,top,2.7);prev=hi
  for pos in [lo-.024,hi+.024]:
   loc=(pos,fixed,(bottom+top)/2) if axis=='x' else (fixed,pos,(bottom+top)/2)
   dim=(.073,thick+.06,top-bottom+.04) if axis=='x' else (thick+.06,.073,top-bottom+.04)
   cube('Opening casing',loc,dim,trim,.0015,'Architecture')
  loc=((lo+hi)/2,fixed,top+.027) if axis=='x' else (fixed,(lo+hi)/2,top+.027)
  dim=(hi-lo+.12,thick+.07,.078) if axis=='x' else (thick+.07,hi-lo+.12,.078)
  cube('Casing head',loc,dim,trim,.0015,'Architecture')
 box(prev,b,0,2.7)
def pw(axis,fixed,a,b,ops=(),ext=False):
 # Plan-space wrapper.
 if axis=='x':wall('x',-fixed,a,b,ops,ext)
 else:wall('y',fixed,-b,-a,[(-hi,-lo,bt,tp) for lo,hi,bt,tp in ops],ext)
def segment(name,a,b,window=True):
 before=set(bpy.data.objects);length=math.dist(a,b)
 wall('x',0,0,length,[(.18,length-.18,.8,2.3)] if window else [],True)
 if window:win_local(name,length/2,0,length-.36,.8,2.3,0)
 angle=math.atan2(-(b[1]-a[1]),b[0]-a[0])
 for o in set(bpy.data.objects)-before:
  co=o.location.copy();o.location=(a[0]+co.x*math.cos(angle)-co.y*math.sin(angle),-a[1]+co.x*math.sin(angle)+co.y*math.cos(angle),co.z);o.rotation_euler.z+=angle
# Window constructed in x/z plane, interior on local -Y side.
def win_local(name,x,y,w,bottom=.8,top=2.3,rot=0):
 before=set(bpy.data.objects)
 for xx in [-w/2,w/2]:cube(name+' black jamb',(xx,0,(top+bottom)/2),(.046,.085,top-bottom),black,.002,'Architecture')
 for zz in [bottom,top,(bottom+top)/2]:cube(name+' black sash',(0,0,zz),(w,.085,.047),black,.002,'Architecture')
 cube(name+' glass',(0,0,(top+bottom)/2),(w-.045,.007,top-bottom-.045),glass,0,'Architecture')
 cube(name+' white sill',(0,0,bottom-.029),(w+.16,.29,.052),trim,.002,'Architecture')
 cube(name+' blind headrail',(0,-.077,top+.04),(w+.1,.08,.06),trim,.002,'Architecture')
 for k in range(8):cube(name+' blind slat',(0,-.08,top-.035-k*.032),(w+.035,.06,.009),trim,.001,'Architecture')
 for xx in [-w*.36,w*.36]:pipe(name+' blind cord',[(xx,-.113,top-.07),(xx,-.113,top-.37)],.0015,trim,'Architecture')
 for o in set(bpy.data.objects)-before:
  co=o.location.copy();o.location=(x+co.x*math.cos(rot)-co.y*math.sin(rot),y+co.x*math.sin(rot)+co.y*math.cos(rot),co.z);o.rotation_euler.z+=rot
# Perimeter and all partition walls, split at rooms to keep lightmap texel density sensible.
pw('x',-3.22,0,3.58,[(.72,1.82,.8,2.3)],True)
pw('y',0,-3.22,-1.47,[(-2.65,-1.93,.8,2.3)],True)
pw('x',-1.47,-.43,0,ext=True);pw('y',-.43,-1.47,-.05,ext=True);pw('x',-.05,-.43,0,ext=True);pw('y',0,-.05,1.74,ext=True);pw('x',1.74,0,2.4,ext=True)
pw('y',3.58,-3.22,0)
pw('x',0,2.4,7.2,[(2.66,3.5,0,2.14),(3.75,4.6,0,2.14)])
pw('y',7.2,-3.25,0,ext=True);pw('x',-4.12,4.56,6.38,[(4.84,6.1,.8,2.3)],True)
segment('BR1 west bay',(3.58,-3.22),(4.56,-4.12));segment('BR1 east bay',(6.38,-4.12),(7.2,-3.25))
pw('y',7.2,0,4.6,[(1.63,3.12,.77,2.3)],True)
pw('y',2.4,1.74,4.6,[(2.98,3.88,0,2.15),(1.76,2.61,.88,2.26)],True)
# Short living/BR2 east wall section above the deck.
pw('y',2.4,0,1.74)
pw('x',4.6,0,5.9,ext=True)
pw('y',0,4.6,8.72,[(6.2,7.18,.8,2.3)],True)
pw('y',3.4,4.6,8)
pw('x',6.3,3.4,5.9)
pw('y',5.9,4.6,6.3,[(4.8,5.65,0,2.12)])
pw('y',5.9,6.3,8,[(7,7.85,0,2.12)])
pw('x',8,0,2.4,[(1.46,2.31,0,2.12)])
pw('x',7.45,2.4,3.4);pw('y',2.4,7.45,8)
pw('x',8,2.4,5.9,[(2.57,3.31,0,2.12)])
pw('y',1,8,9.18);pw('x',8.72,0,1)
pw('y',7.2,4.6,9.18,[(8.22,9.07,0,2.13)],True)
pw('x',9.18,1,7.2,[(2.1,2.96,0,2.12)])
pw('y',0,8.72,13,[(10.02,10.81,.8,2.3),(11.25,12.09,.8,2.3)],True)
pw('y',3.06,9.18,13,ext=True);pw('x',13,0,3.06,ext=True)
# Deck boundary is not photographed: neutral weathered boards and rail.
pw('y',0,2.45,4.6,ext=True)
# Floor polygons avoid the courtyard and preserve the rear bay and corner recess.
rooms={
 'living':[(2.4,0),(7.2,0),(7.2,4.6),(2.4,4.6)],
 'bed1':[(3.58,-3.22),(4.56,-4.12),(6.38,-4.12),(7.2,-3.25),(7.2,0),(3.58,0)],
 'bed2':[(0,-3.22),(3.58,-3.22),(3.58,0),(2.4,0),(2.4,1.74),(0,1.74),(0,-.05),(-.43,-.05),(-.43,-1.47),(0,-1.47)],
 'bed3':[(0,4.6),(3.4,4.6),(3.4,7.45),(2.4,7.45),(2.4,8),(1,8),(1,8.72),(0,8.72)],
 'bed4':[(0,8.72),(1,8.72),(1,9.18),(3.06,9.18),(3.06,13),(0,13)],
 'hall':[(5.9,4.6),(7.2,4.6),(7.2,9.18),(1,9.18),(1,8),(5.9,8)],
 'bath1':[(3.4,6.3),(5.9,6.3),(5.9,8),(3.4,8)],
 'bath2':[(3.4,4.6),(5.9,4.6),(5.9,6.3),(3.4,6.3)],
 'laundry':[(2.4,7.45),(3.4,7.45),(3.4,8),(2.4,8)],
 'deck':[(0,2.45),(2.4,2.45),(2.4,4.6),(0,4.6)]}
# Use Blender tessellation to clip each plank against concave room polygons exactly.
from mathutils.geometry import tessellate_polygon

def clip(poly,axis,bound,greater):
 out=[]
 for i,p in enumerate(poly):
  q=poly[(i+1)%len(poly)];a=p[axis]>=bound if greater else p[axis]<=bound;b=q[axis]>=bound if greater else q[axis]<=bound
  if a:out.append(p)
  if a!=b:
   t=(bound-p[axis])/(q[axis]-p[axis]);out.append((p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t))
 return out

def surface(name,poly,z,mat):
 mesh=bpy.data.meshes.new(name);verts=[(x,-p,z) for x,p in poly];mesh.from_pydata(verts,[],[list(reversed(range(len(verts))))]);mesh.update()
 o=bpy.data.objects.new(name,mesh);COL['Architecture'].objects.link(o);mesh.materials.append(mat)
 return o
for room,poly in rooms.items():
 floorMat=floorTile if room.startswith('bath') else deckmat if room=='deck' else wood
 surface(room+' subfloor',poly,-.013,grout if room.startswith('bath') else woodEdge)
 ceiling=surface(room+' ceiling',poly,2.7,paint)
 # Ceiling must face downward.
 for p in ceiling.data.polygons:p.flip()
 if room=='deck':continue
 triangles=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]])
 x0=min(x for x,y in poly);x1=max(x for x,y in poly);y0=min(y for x,y in poly);y1=max(y for x,y in poly)
 w=.305 if room.startswith('bath') else .19;length=.61 if room.startswith('bath') else 1.25
 ix=0;x=x0
 while x<x1-.001:
  y=y0-(ix%3)*length/3
  while y<y1:
   pieces=[]
   for tri in triangles:
    p=[poly[v] if isinstance(v,int) else (v.x,v.y) for v in tri]
    for axis,bound,g in [(0,x+.0007,True),(0,x+w-.0007,False),(1,y+.0007,True),(1,y+length-.0007,False)]:
     if p:p=clip(p,axis,bound,g)
    if len(p)>=3:pieces.append(p)
   board=rng.randrange(6);offset=rng.random()*.11
   for p in pieces:
    o=surface(room+' floor plank' if not room.startswith('bath') else room+' floor tile',p,0,floorMat)
    uv=o.data.uv_layers.new(name='UVMap')
    for loop in o.data.loops:
     v=o.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((board+.02+(v.x-x)/w*.96)/6,.02+(-v.y-y)/length*.86+offset)
   y+=length
  x+=w;ix+=1
# Windows, including the bay required by the plan but not confirmed in a photograph.
win_local('BR2 rear window',1.27,3.22,1.1)
win_local('BR2 side window',0,2.29,.72,rot=math.pi/2)
win_local('BR1 rear bay window',5.47,4.12,1.26)
window_xplane('Living window',7.2,-2.375,1.49,.77,2.3);window_xplane('Deck-side window',2.4,-2.185,.85,.88,2.26)
win_local('BR3 side window',0,-6.69,.98,rot=math.pi/2)
for z,w in [(10.415,.79),(11.67,.84)]:win_local('BR4 side window',0,-z,w,rot=math.pi/2)
paneled_door('Deck five-panel door',(2.38,-3.43,0),.85,-math.pi/2)
paneled_door('Unit entry door',(7.18,-8.645,0),.83,math.pi/2)
# Bedroom doors are open, using the two-panel face seen in the bedroom photos.
def two_panel(name,x,z,w=.78,rot=0,group='Bedrooms',height=2.1):
 before=set(bpy.data.objects);cube(name+' leaf',(0,0,height/2),(w,.04,height),trim,.002,group)
 for cz,ch in [(height*.26,height*.36),(height*.74,height*.4)]:
  cube(name+' recessed panel',(0,.023,cz),(w-.15,.01,ch),white,.005,group)
  for xx in [-w/2+.07,w/2-.07]:cube(name+' panel stile',(xx,.03,cz),(.018,.012,ch+.02),trim,.003,group)
  for zz in [cz-ch/2,cz+ch/2]:cube(name+' panel rail',(0,.03,zz),(w-.12,.012,.018),trim,.003,group)
 cylinder(name+' lever rose',(w*.35,.05,1.01),.03,.016,steel,(math.pi/2,0,0),group)
 pipe(name+' lever',[(w*.35,.05,1.01),(w*.35,.10,1.01),(w*.35-.11,.1,1.01)],.009,steel,group)
 for o in set(bpy.data.objects)-before:
  co=o.location.copy();o.location=(x+co.x*math.cos(rot)-co.y*math.sin(rot),-z+co.x*math.sin(rot)+co.y*math.cos(rot),co.z);o.rotation_euler.z+=rot
for name,x,z,r in [('BR2 open door',2.69,-.42,math.pi/2),('BR1 open door',3.79,-.42,math.pi/2),('BR3 open door',1.50,7.58,math.pi/2),('BR4 open door',2.94,9.60,math.pi/2),('BA2 open door',5.48,4.84,0),('BA1 open door',5.48,7.81,0)]:two_panel(name,x,z,rot=r)
# Closets: real recess, shelf and hanging rail, and staggered bypass door leaves.
def closet(name,x,z,w,rot=0,depth=.55,open_half=False):
 before=set(bpy.data.objects)
 for xx in [-w/2,w/2]:cube(name+' side',(xx,-depth/2,1.35),(.085,depth,2.7),paint,0,'Bedrooms')
 cube(name+' header',(0,0,2.45),(w+.08,.11,.5),paint,0,'Bedrooms')
 cube(name+' shelf',(0,-depth/2,1.85),(w,.48,.023),trim,.001,'Bedrooms')
 pipe(name+' hanging rod',[(-w/2+.05,-.27,1.73),(w/2-.05,-.27,1.73)],.012,chrome,'Bedrooms')
 for offset in [-w/4,w/4]:
  if open_half and offset>0:continue
  # A closet handle is a recessed finger pull rather than a projecting lever.
  leaf=cube(name+' bypass leaf',(offset,.015 if offset<0 else .055,1.06),(w/2+.025,.033,2.12),trim,.002,'Bedrooms')
  for zz,hh in[(.52,.72),(1.58,.77)]:cube(name+' raised panel',(offset,.04 if offset<0 else .08,zz),(w/2-.11,.014,hh),white,.005,'Bedrooms')
  cylinder(name+' recessed pull',(offset+w/4-.08,.066 if offset<0 else .106,1),.023,.003,steel,(math.pi/2,0,0),'Bedrooms')
 for o in set(bpy.data.objects)-before:
  co=o.location.copy();o.location=(x+co.x*math.cos(rot)-co.y*math.sin(rot),-z+co.x*math.sin(rot)+co.y*math.cos(rot),co.z);o.rotation_euler.z+=rot
closet('BR1 wardrobe',6.17,-.60,1.9,rot=0)
closet('BR2 wardrobe',3.00,-2.12,1.78,rot=math.pi/2,open_half=True)
closet('BR3 closet',.5,8.05,.82,rot=math.pi)
closet('BR4 closet',.5,9.27,.82,rot=0)
# Baseboard heaters visible in the bedrooms, sockets, smoke alarms and flush glass ceiling lights.
def heater(name,x,z,rot=0):
 before=set(bpy.data.objects);cube(name,(0,0,.2),(.86,.09,.19),trim,.004,'Bedrooms')
 for h in [.19,.225,.26]:cube(name+' louver',(0,.05,h),(.77,.006,.012),rubber,.001,'Bedrooms')
 for o in set(bpy.data.objects)-before:
  co=o.location.copy();o.location=(x+co.x*math.cos(rot)-co.y*math.sin(rot),-z+co.x*math.sin(rot)+co.y*math.cos(rot),co.z);o.rotation_euler.z+=rot
for name,x,z,rot in [('BR1',6.9,-1.5,math.pi/2),('BR2',1.5,1.64,0),('BR3',3.31,6.8,math.pi/2),('BR4',1.65,9.27,math.pi)]:heater(name+' baseboard heater',x,z,rot)
for room,x,z in [('BR1',5.55,-2.0),('BR2',1.5,-1.6),('BR3',1.65,6.2),('BR4',1.5,11.0),('Entry',3.9,8.57)]:
 cylinder(room+' flush light rim',(x,-z,2.65),.18,.044,chrome,group='Lighting');cylinder(room+' opal glass diffuser',(x,-z,2.622),.16,.035,emission,group='Lighting');area(room+' ceiling light',(x,-z,2.59),(x,-z,0),45,.31,(1,.91,.80))
 cylinder(room+' smoke detector',(x+.45,-z+.5,2.674),.057,.036,trim,group='Bedrooms')
# Cool daylight enters through the actual aperture direction.
for name,loc,target,power,w in [('BR2 rear',(1.27,3.09,1.65),(1.6,.2,.9),210,1.05),('BR2 side',(.14,2.29,1.65),(2,1.5,1),120,.68),('BR1 bay',(5.47,3.98,1.65),(5.4,.7,1),260,1.2),('BR1 west bay',(4.10,3.55,1.65),(5.5,1.4,.8),105,.9),('BR1 east bay',(6.69,3.56,1.65),(5.4,1.4,.8),105,.9),('BR3 window',(.15,-6.69,1.65),(2.5,-6.3,.9),180,.92),('BR4 window A',(.15,-10.415,1.65),(2.6,-10.5,.9),140,.73),('BR4 window B',(.15,-11.67,1.65),(2.6,-11.5,.9),150,.78)]:area(name+' daylight',loc,target,power,w,(.85,.92,1),1.3)
for x,z,rot in [(1.4,-3.13,math.pi),(2.8,1.65,0),(3.49,-1.1,math.pi/2),(5.2,-.09,0),(.09,5.5,-math.pi/2),(2.5,4.7,math.pi),(1.5,12.9,0),(2.97,11.7,math.pi/2),(6.0,8.1,-math.pi/2)]:outlet(x,-z,.29,rot)
# Bathroom fixtures are modeled locally with the tub along the left side of the plan.
def bath(name,zmin):
 # zmin northern wall; fixtures reverse between BA1 / BA2 as in photos 7 and 8.
 front=zmin+.1 if name=='BA2' else zmin+1.6
 back=zmin+1.6 if name=='BA2' else zmin+.1
 # Tub spans depth of room, apron facing the toilet/vanity side.
 tub=cube(name+' porcelain bathtub',(3.86,-(zmin+.85),.275),(.78,1.56,.55),ceramic,.055,'Bathrooms')
 cutter=cube('Tub bowl cutter',(3.86,-(zmin+.85),.44),(.60,1.35,.42),ceramic,.095,'Bathrooms')
 bpy.context.view_layer.objects.active=cutter
 for mod in list(cutter.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 mod=tub.modifiers.new('True recessed tub bowl','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter;bpy.context.view_layer.objects.active=tub;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 for j in range(5):
  for k in range(4):
   cube(name+' surround wall tile',(3.47,-(zmin+.12+j*.305),.6+k*.52),(.018,.301,.516),tile,.0007,'Bathrooms')
 for zz in [zmin+.08,zmin+1.62]:
  for j in range(3):
   for k in range(4):cube(name+' end wall tile',(3.59+j*.27,-zz,.6+k*.52),(.266,.019,.516),tile,.0007,'Bathrooms')
 # Glass panels in actual chrome frame; thin panels preserve transparency in Cycles.
 for zz in [zmin+.08,zmin+1.62]:cube(name+' shower upright',(4.27,-zz,1.31),(.035,.035,1.60),chrome,.005,'Bathrooms')
 for h in [.55,2.1]:pipe(name+' shower track',[(4.27,-(zmin+.07),h),(4.27,-(zmin+1.63),h)],.018,chrome,'Bathrooms')
 for j in range(2):cube(name+' sliding shower glass',(4.265+j*.017,-(zmin+.46+j*.76),1.32),(.007,.78,1.52),glass,.001,'Bathrooms')
 pipe(name+' shower towel handle',[(4.31,-(zmin+.33),1.15),(4.34,-(zmin+.33),1.15),(4.34,-(zmin+.92),1.15),(4.31,-(zmin+.92),1.15)],.009,chrome,'Bathrooms')
 # Shower head and valve on inner short wall.
 sy=-(zmin+.12)
 cylinder(name+' mixer',(3.86,sy-.025,.96),.068,.018,chrome,(math.pi/2,0,0),'Bathrooms')
 pipe(name+' tub spout',[(3.86,sy,.7),(3.86,sy-.16,.7),(3.86,sy-.18,.68)],.021,chrome,'Bathrooms')
 pipe(name+' shower arm',[(3.86,sy,2.10),(3.86,sy-.15,2.1),(3.86,sy-.20,2.04)],.011,chrome,'Bathrooms')
 cylinder(name+' shower rose',(3.86,sy-.20,2.025),.063,.019,chrome,group='Bathrooms')
 # Toilet ceramic shapes with a hollow bowl and separate seat/lid.
 tz=back+(.31 if name=='BA1' else -.31);tx=4.63
 def ellipsoid(n,loc,scale,mat):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc);o=bpy.context.object;o.name=name+' '+n;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
  for p in o.data.polygons:p.use_smooth=True
  return put(o,'Bathrooms')
 ellipsoid('toilet pedestal',(tx,-tz,.19),(.145,.19,.19),ceramic);ellipsoid('toilet bowl',(tx,-tz,.33),(.19,.29,.16),ceramic)
 ellipsoid('toilet seat shadow',(tx,-tz,.451),(.184,.275,.015),rubber);ellipsoid('toilet closed lid',(tx,-tz,.467),(.186,.275,.018),ceramic)
 cube(name+' toilet cistern',(tx,-back,.56),(.38,.17,.40),ceramic,.045,'Bathrooms');cube(name+' cistern lid',(tx,-back,.771),(.40,.19,.035),ceramic,.017,'Bathrooms')
 # Vanity faces into the bathroom (north/south), as opposed to the side-facing tub.
 vy=-(back+(.22 if name=='BA1' else -.22));facing=-1 if name=='BA1' else 1;vx=5.40
 cube(name+' vanity cabinet',(vx,vy,.445),(.80,.50,.80),white,.004,'Bathrooms')
 for dx in [-.198,.198]:
  cube(name+' vanity door',(vx+dx,vy+facing*.265,.42),(.385,.027,.59),trim,.003,'Bathrooms');cube(name+' vanity inset',(vx+dx,vy+facing*.282,.42),(.285,.011,.46),white,.003,'Bathrooms')
  pipe(name+' vanity pull',[(vx+dx+(.13 if dx<0 else -.13),vy+facing*.31,.38),(vx+dx+(.13 if dx<0 else -.13),vy+facing*.31,.56)],.0055,steel,'Bathrooms')
 top=cube(name+' white quartz vanity top',(vx,vy,.869),(.85,.55,.044),ceramic,.005,'Bathrooms')
 cut=cube('Vanity basin cut',(vx,vy+facing*.025,.87),(.47,.30,.16),ceramic,.035,'Bathrooms');bpy.context.view_layer.objects.active=cut
 for mod in list(cut.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 mod=top.modifiers.new('Undermount basin opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=top;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
 cube(name+' basin bottom',(vx,vy,.76),(.46,.30,.025),ceramic,.025,'Bathrooms')
 for dx in [-.23,.23]:cube(name+' basin side',(vx+dx,vy,.817),(.016,.30,.10),ceramic,.004,'Bathrooms')
 for dy in [-.15,.15]:cube(name+' basin side',(vx,vy+dy,.817),(.46,.016,.10),ceramic,.004,'Bathrooms')
 fy=vy-facing*.20;pipe(name+' chrome basin faucet',[(vx,fy,.88),(vx,fy,1.035),(vx,fy+facing*.13,1.035),(vx,fy+facing*.13,1.01)],.018,chrome,'Bathrooms')
 pipe(name+' faucet lever',[(vx,fy,1.06),(vx,fy+facing*.1,1.075)],.007,chrome,'Bathrooms')
 my=-back+facing*.025
 cube(name+' framed mirror',(vx,my,1.56),(.83,.04,.72),trim,.003,'Bathrooms');cube(name+' mirror glass',(vx,my+facing*.024,1.56),(.70,.005,.59),mirror,.001,'Bathrooms')
 for h in [1.17,1.97]:cube(name+' mirror cornice',(vx,my+facing*.027,h),(.91,.09,.045),trim,.003,'Bathrooms')
 cube(name+' vanity light',(vx,my+facing*.07,2.18),(.58,.065,.09),emission,.009,'Lighting');area(name+' vanity illumination',(vx,my+facing*.12,2.15),(vx,vy+facing*.6,.9),75,.50,(1,.93,.86),.12)
 area(name+' ceiling illumination',(4.75,-(zmin+.85),2.58),(4.75,-(zmin+.85),0),62,.26,(1,.92,.84))
bath('BA2',4.6);bath('BA1',6.3)
# Stacked GE-style laundry, constrained by the shallow plan closet: depth remains inferred.
cube('Laundry closet back',(2.90,-7.46,1.35),(.98,.1,2.7),paint,0,'Laundry')
cube('Washer cabinet',(2.91,-7.76,.49),(.67,.59,.91),white,.016,'Laundry')
cube('Washer top lid',(2.91,-7.75,.963),(.60,.53,.036),trim,.012,'Laundry')
cube('Stacked dryer casing',(2.91,-7.77,1.80),(.67,.55,.78),white,.024,'Laundry')
cube('Dryer door shadow',(2.91,-8.053,1.85),(.55,.012,.55),rubber,.05,'Laundry')
cube('Dryer front door',(2.91,-8.064,1.85),(.54,.025,.54),trim,.05,'Laundry')
cube('Laundry center control panel',(2.91,-8.058,1.31),(.65,.039,.18),white,.008,'Laundry')
for x,r in [(2.68,.045),(2.87,.031),(3.09,.04)]:cylinder('Laundry rotary control',(x,-8.09,1.31),r,.025,steel,(math.pi/2,0,0),'Laundry')
pipe('Dryer recessed handle',[(2.68,-8.088,1.90),(2.68,-8.088,2.08)],.014,trim,'Laundry')
# Deck boards and rail; no invented furnished staging.
for j in range(14):cube('Covered deck board',(1.2,-(2.50+j*.15),-.005),(2.38,.145,.04),deckmat,.001,'Deck')
for x in [.08,2.30]:cube('Deck railing post',(x,-2.48,.55),(.075,.075,1.1),trim,.002,'Deck')
cube('Deck top rail',(1.2,-2.48,1.1),(2.38,.08,.075),trim,.003,'Deck')
for x in [.2+i*.14 for i in range(15)]:cube('Deck baluster',(x,-2.48,.55),(.03,.03,1.05),trim,.001,'Deck')
# Named cameras and reference notes inside the editable file.
for name,loc,target,lens in [
 ('04 — bedroom 2 toward corner / photos 5–6',(2.23,.40,1.56),(.70,2.72,1.25),20),
 ('05 — bedroom 2 toward closet',(0.43,2.59,1.58),(3.1,.20,1.25),20),
 ('06 — bedroom 1 rear bay / plan-led',(4.10,.52,1.60),(5.65,3.5,1.25),21),
 ('07 — bedroom 3 / photo 11 tentative',(2.48,-7.18,1.58),(.54,-5.35,1.1),21),
 ('08 — bedroom 4 toward windows / photos 9–10',(2.48,-9.63,1.58),(.50,-11.90,1.12),21),
 ('09 — bedroom 4 toward laundry',(1.02,-12.34,1.58),(2.27,-8.4,1.23),20),
 ('10 — bathroom 1 / photo 7',(5.72,-7.53,1.56),(4.42,-6.90,1.08),19),
 ('11 — bathroom 2 / photo 8',(5.72,-4.99,1.56),(4.43,-5.86,1.06),19),
 ('12 — entry and laundry',(5.95,-8.6,1.57),(2.7,-8.04,1.20),22)]:camera(name,loc,target,lens)
scene.camera=bpy.data.objects['01 — living toward kitchen (photo 1)']
notes='''FULL UNIT PHOTO CROSS-CHECK\nThe supplied full plan governs room adjacency, the BR1 rear bay, BR2 recess, entry and hall.\nPhotos 1–3: strong kitchen/living match; appliance order retained.\nPhotos 5–6: probable BR2, using corner windows, wall recess, closet and living sightline.\nPhotos 9–10: probable BR4, two west windows and laundry visible across hall.\nPhoto 11: provisional BR3. Photo 12 overlaps the two-window bedroom description and does not establish a fourth distinct bedroom.\nBR1 bay is plan-led; no supplied photo conclusively shows its full geometry.\nPhotos 7–8: mirrored bathroom fixture arrangements and finish details.\nLaundry closet depth and exact position, deck finishes, window dimensions, heights and scale remain estimates.\n1,140 sq ft is user-reported, not independently measured. This is a modeled reconstruction, not a scan.\n'''
text=bpy.data.texts.get('READ ME — reconstruction evidence') or bpy.data.texts.new('READ ME — reconstruction evidence');text.clear();text.write(notes)
(ROOT/'FULL_UNIT_EVIDENCE.md').write_text(notes)
for i in range(1,15):
 if i==13:continue
 path=ROOT.parent/'public'/'references'/f'{i:02}.png'
 im=bpy.data.images.load(str(path),check_existing=True);im.name=f'REFERENCE {i:02}';im.pack();im.use_fake_user=True
for o in scene.objects:
 if o.type=='LIGHT':
  o.visible_glossy=False;o.visible_transmission=False;o.visible_camera=False
# Simplified solid-object collision volumes for the free-walk browser mode.
colliders=[]
for o in scene.objects:
 if o.type!='MESH':continue
 if not any(t in o.name.lower() for t in ['plaster wall','solid leaf','open door leaf','wardrobe side','wardrobe bypass','closet bypass','vanity cabinet','bathtub','toilet bowl','refrigerator body','range body','base cabinet carcass','dishwasher body','washer cabinet']):continue
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]
 if max(v.z for v in pts)<.12 or min(v.z for v in pts)>1.7:continue
 colliders.append({'name':o.name,'min':[min(v.x for v in pts),-max(v.y for v in pts)],'max':[max(v.x for v in pts),-min(v.y for v in pts)]})
dest=ROOT.parent/'public'/'models'/'full';dest.mkdir(parents=True,exist_ok=True)
(dest/'collision.json').write_text(json.dumps({'rooms':rooms,'solids':colliders}))
scene['render_stage']='Full unit: all four bedrooms, two bathrooms, kitchen, living, entry/laundry and inferred covered deck.'
scene['reference_basis']=notes
scene.cycles.samples=160;scene.cycles.use_denoising=True;scene.cycles.device='GPU'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'renders'/'full-unit-kitchen.png')
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.overlay.show_overlays=False;a.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'2861-california-unit-4-full.blend'))
# Low-cost composition checks precede the final lighting export.
scene.cycles.samples=40;scene.render.resolution_percentage=55
for prefix in ['04','06','08','10','11','12']:
 scene.camera=next(o for o in COL['Cameras'].objects if o.name.startswith(prefix+' —'))
 scene.render.filepath=str(ROOT/'renders'/f'full-check-{prefix}.png');bpy.ops.render.render(write_still=True)
print('FULL_UNIT_BUILD_COMPLETE',flush=True)
