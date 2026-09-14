"""Render full Cycles panoramas; JPGs already have Blender's AgX display transform."""
import bpy, math, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;DEST=ROOT.parent/'public'/'daylight-tour';DEST.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4-daylight.blend'))
s=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
s.cycles.device='GPU';s.cycles.samples=192;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.015
s.render.resolution_x=4096;s.render.resolution_y=2048;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=96;s.render.image_settings.color_mode='RGB'
data=bpy.data.cameras.new('Rendered tour panorama');data.type='PANO';data.panorama_type='EQUIRECTANGULAR'
cam=bpy.data.objects.new('Rendered tour panorama',data);s.collection.objects.link(cam);cam.rotation_euler=(math.pi/2,0,0);s.camera=cam
# Positions are navigable floor positions in Three.js coordinates, not exterior or inside furniture.
views=[
 {'id':'living','room':'living','name':'Living / dining','position':[6.15,1.58,1.35],'target':[4.0,1.3,4.0],'links':['kitchen','bed1','bed2','hall','deck']},
 {'id':'kitchen','room':'living','name':'Kitchen','position':[5.1,1.58,3.10],'target':[3.9,1.35,4.3],'links':['living','hall','deck']},
 {'id':'bed1','room':'bed1','name':'Bedroom 1 · rear bay','position':[5.35,1.58,-1.8],'target':[5.5,1.3,-4.0],'links':['living']},
 {'id':'bed2','room':'bed2','name':'Bedroom 2 · rear corner','position':[1.6,1.58,-1.15],'target':[.6,1.3,-2.9],'links':['living']},
 {'id':'bed3','room':'bed3','name':'Bedroom 3','position':[1.75,1.58,6.35],'target':[.2,1.3,6.5],'links':['entry']},
 {'id':'bed4','room':'bed4','name':'Bedroom 4 · entry side','position':[1.55,1.58,11.0],'target':[.1,1.3,11.4],'links':['entry']},
 {'id':'bath1','room':'bath1','name':'Bathroom 1','position':[5.25,1.56,7.4],'target':[3.9,1.2,6.9],'links':['hall']},
 {'id':'bath2','room':'bath2','name':'Bathroom 2','position':[5.25,1.56,5.15],'target':[3.9,1.2,5.8],'links':['hall']},
 {'id':'hall','room':'hall','name':'Hallway','position':[6.55,1.58,5.9],'target':[6.4,1.3,2.8],'links':['living','bath1','bath2','entry']},
 {'id':'entry','room':'hall','name':'Entry / laundry','position':[4.65,1.58,8.55],'target':[2.05,1.22,8.5],'links':['hall','bed3','bed4']},
 {'id':'deck','room':'deck','name':'Covered deck · inferred','position':[1.35,1.58,3.35],'target':[1.0,1.15,2.45],'links':['living']},
]
# Doorway anchors keep links attached to their actual direction, avoiding markers through walls.
anchors={
 'living:bed1':[4.17,1.1,0],'living:bed2':[3.08,1.1,0],'living:hall':[6.55,1.1,4.6],'living:deck':[2.4,1.1,3.43],
 'bed1:living':[4.17,1.1,0],'bed2:living':[3.08,1.1,0],'bed3:entry':[1.89,1.1,8],'bed4:entry':[2.53,1.1,9.18],
 'bath1:hall':[5.9,1.1,7.42],'bath2:hall':[5.9,1.1,5.23],
 'hall:bath1':[5.9,1.1,7.42],'hall:bath2':[5.9,1.1,5.23],'hall:entry':[6.55,1.1,8.55],
 'entry:bed3':[1.89,1.1,8],'entry:bed4':[2.53,1.1,9.18],'entry:hall':[6.55,1.1,8.55],
 'deck:living':[2.4,1.1,3.43],'kitchen:deck':[2.4,1.1,3.43],'kitchen:hall':[6.55,1.1,4.6]}
(DEST/'manifest.json').write_text(json.dumps({'views':views,'anchors':anchors,'width':4096,'height':2048,'samples':192,'color':'Blender AgX display-referred sRGB; no additional tone mapping','movement':'Fixed camera positions with room links; transitions are fades, not continuous parallax','lighting':'Daylight sun/sky with indirect bounce; exterior and sun orientation are illustrative','exposure_ev':float(s.view_settings.exposure)},indent=2))
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for view in views:
 if selected and view['id'] not in selected:continue
 x,h,z=view['position'];cam.location=(x,-z,h);s.render.filepath=str(DEST/(view['id']+'.jpg'))
 print('PANORAMA_START',view['id'],flush=True);bpy.ops.render.render(write_still=True);print('PANORAMA_DONE',view['id'],flush=True)
 if view['id'] in ['living','bed1','hall']:
  zone={'living':'living','bed1':'rear','hall':'front'}[view['id']]
  dest=ROOT.parent/'public'/'models'/'daylight';dest.mkdir(parents=True,exist_ok=True)
  raw=ROOT/'textures'/f'{zone}-reflections-raw.exr'
  s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='16';s.render.image_settings.exr_codec='ZIP'
  bpy.data.images['Render Result'].save_render(str(raw),scene=s)
  im=bpy.data.images.load(str(raw));im.scale(1536,768);im.save_render(str(dest/f'{zone}-reflections.exr'),scene=s);bpy.data.images.remove(im)
  s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=96

