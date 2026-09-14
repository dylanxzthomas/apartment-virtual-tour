import bpy,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4-full.blend'))
s=bpy.context.scene
for o in s.objects:
 if o.type in {'MESH','CURVE'} and ('ceiling' in o.name.lower() or any(c.name in {'Exterior','Lighting'} for c in o.users_collection)):o.hide_render=True
cam=bpy.data.objects.new('Plan verification camera',bpy.data.cameras.new('Plan verification camera'));s.collection.objects.link(cam);cam.data.type='ORTHO';cam.data.ortho_scale=19;cam.location=(3.6,-4.4,25);s.camera=cam
s.cycles.samples=32;s.cycles.device='GPU';s.render.resolution_x=960;s.render.resolution_y=1700;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(ROOT/'renders'/'full-plan-check.png')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=2;s.view_settings.exposure=0
bpy.ops.render.render(write_still=True)
