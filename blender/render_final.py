import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4.blend'))
s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
bpy.ops.wm.save_userpref()
s.cycles.device='GPU';s.cycles.samples=96
s.render.resolution_percentage=80
s.render.filepath=str(ROOT/'renders'/'living-kitchen-preview.png')
bpy.ops.render.render(write_still=True)
s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'2861-california-unit-4.blend'))
