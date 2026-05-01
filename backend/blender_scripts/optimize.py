import bpy
import sys
import os

# Get arguments
argv = sys.argv
argv = argv[argv.index("--") + 1:] # get all args after "--"

if len(argv) < 3:
    print("Usage: blender -b -P optimize.py -- <input_file> <output_file> <decimation_ratio>")
    sys.exit(1)

input_file = argv[0]
output_file = argv[1]
decimation_ratio = float(argv[2])

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import file
ext = os.path.splitext(input_file)[1].lower()
if ext == '.obj':
    bpy.ops.wm.obj_import(filepath=input_file)
elif ext == '.fbx':
    bpy.ops.import_scene.fbx(filepath=input_file)
elif ext in ['.glb', '.gltf']:
    bpy.ops.import_scene.gltf(filepath=input_file)
else:
    print(f"Unsupported input format: {ext}")
    sys.exit(1)

# Apply decimate modifier to all meshes
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        mod = obj.modifiers.new(name='Decimate', type='DECIMATE')
        mod.ratio = decimation_ratio
        bpy.ops.object.modifier_apply(modifier=mod.name)

# Export file
out_ext = os.path.splitext(output_file)[1].lower()
if out_ext == '.obj':
    bpy.ops.wm.obj_export(filepath=output_file)
elif out_ext == '.fbx':
    bpy.ops.export_scene.fbx(filepath=output_file)
elif out_ext in ['.glb', '.gltf']:
    bpy.ops.export_scene.gltf(filepath=output_file, export_format='GLB')
else:
    print(f"Unsupported output format: {out_ext}")
    sys.exit(1)

print(f"Successfully processed and exported to {output_file}")
