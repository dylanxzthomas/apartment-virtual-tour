import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent;DEST=ROOT.parent/'public'/'models'/'refined'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6
cam=bpy.data.objects.new('Compositor camera',bpy.data.cameras.new('Compositor camera'));s.collection.objects.link(cam);s.camera=cam
s.render.resolution_x=3072;s.render.resolution_y=3072;s.render.resolution_percentage=100
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='16';s.render.image_settings.exr_codec='ZIP'
s.render.filepath=str(DEST/'diffuse-lightmap-clean.exr')
g=bpy.data.node_groups.new('Lightmap denoising','CompositorNodeTree');s.compositing_node_group=g
g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
image=g.nodes.new('CompositorNodeImage');image.image=bpy.data.images.load(str(ROOT/'textures'/'diffuse-lightmap-raw.exr'))
denoise=g.nodes.new('CompositorNodeDenoise')
out=g.nodes.new('NodeGroupOutput');g.links.new(image.outputs['Image'],denoise.inputs['Image']);g.links.new(denoise.outputs['Image'],out.inputs['Image'])
bpy.ops.render.render(write_still=True)
clean=bpy.data.images.load(str(DEST/'diffuse-lightmap-clean.exr'));clean.scale(2048,2048);clean.save_render(str(DEST/'diffuse-lightmap-clean.exr'),scene=s)
print('DENOISED_LIGHTMAP_COMPLETE',flush=True)
