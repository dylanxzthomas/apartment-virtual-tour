"""Keep the editable scene and textures; reference photographs remain in the web gallery."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'2861-california-unit-4-daylight.blend'))
refs=[im for im in bpy.data.images if im.name.startswith('REFERENCE ')]
assert all(im.use_fake_user and im.users==1 for im in refs),'A reference is used by the model; preserve it.'
for im in refs:bpy.data.images.remove(im)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT.parent/'public/models/2861-california-unit-4.blend'),compress=True)
print('DOWNLOAD_READY',len(refs),'unreferenced gallery images omitted',flush=True)
