import bpy
import sys
import os
import math
from mathutils import Vector

# Get arguments
argv = sys.argv
argv = argv[argv.index("--") + 1:] # get all args after "--"

if len(argv) < 2:
    print("Usage: blender -b -P render_thumbnails.py -- <input_file> <output_dir>")
    sys.exit(1)

input_file = argv[0]
output_dir = argv[1]

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

# Setup rendering
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderEngine.__subclasses__()] else 'BLENDER_EEVEE'
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.film_transparent = True

# Calculate bounding box of all meshes
min_coord = Vector((float("inf"), float("inf"), float("inf")))
max_coord = Vector((float("-inf"), float("-inf"), float("-inf")))

mesh_objects = []
for obj in scene.objects:
    if obj.type == 'MESH':
        mesh_objects.append(obj)
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        for corner in bbox_corners:
            for i in range(3):
                min_coord[i] = min(min_coord[i], corner[i])
                max_coord[i] = max(max_coord[i], corner[i])

if not mesh_objects:
    print("No meshes found in file.")
    sys.exit(1)

center = (min_coord + max_coord) / 2
size = max_coord - min_coord
max_size = max(size)

# Create an Empty object to act as the parent for all meshes
bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
parent_empty = bpy.context.object

# Parent all meshes to the Empty, preserving their current transforms
for obj in mesh_objects:
    obj.parent = parent_empty
    obj.matrix_parent_inverse = parent_empty.matrix_world.inverted()

# Center the Empty (and thereby all meshes) to the origin
parent_empty.location = (0, 0, 0)

# Add camera
cam_distance = max_size * 2.0  # Safe distance
bpy.ops.object.camera_add(location=(0, -cam_distance, 0), rotation=(math.radians(90), 0, 0))
camera = bpy.context.object
scene.camera = camera

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, -5, 5))
sun = bpy.context.object
sun.data.energy = 2.0

base_name = os.path.splitext(os.path.basename(input_file))[0]

views = {
    "front": (0, 0, 0),
    "side": (0, 0, math.radians(90)),
    "top": (math.radians(-90), 0, 0),
    "iso": (math.radians(-45), 0, math.radians(45))
}

for view_name, rotation in views.items():
    # Rotate the parent Empty instead of individual meshes
    parent_empty.rotation_euler = rotation

    scene.render.filepath = os.path.join(output_dir, f"{base_name}_{view_name}.png")
    bpy.ops.render.render(write_still=True)

print(f"Successfully rendered thumbnails to {output_dir}")
