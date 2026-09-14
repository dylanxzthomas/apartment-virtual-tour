import bpy,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4-daylight.blend'))
s=bpy.context.scene;s.cycles.device='CPU';s.cycles.samples=24;s.cycles.adaptive_threshold=.08;s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x=640;s.render.resolution_y=480;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for prefix in ['10','11']:
 s.camera=next(o for o in s.objects if o.type=='CAMERA' and o.name.startswith(prefix+' —'));s.render.filepath=str(ROOT/'renders'/f'daylight-check-{prefix}.png');bpy.ops.render.render(write_still=True);print('DAYLIGHT_AUX_DONE',prefix,flush=True)
