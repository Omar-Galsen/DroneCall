import bpy
import os
from mathutils import Vector

# DroneCall Soldier Builder
# Creates a clean tactical-soldier blockout and exports Unity-ready FBX.
# Designed as a robust fallback that works without MPFB installed.

OUT_DIR = os.path.join(os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd(), "Exports")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_BLEND = os.path.join(OUT_DIR, "Soldier_Master.blend")
OUT_FBX = os.path.join(OUT_DIR, "Soldier_GameReady.fbx")

# -----------------------------
# Utilities
# -----------------------------
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.armatures):
        pass

def mat(name, color, metallic=0.0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m

def add_primitive(name, kind, loc, scale, material=None, rotation=(0,0,0)):
    if kind == "cube":
        bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rotation)
    elif kind == "uvsphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=loc, rotation=rotation)
    elif kind == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, location=loc, rotation=rotation)
    else:
        raise ValueError(kind)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        o.data.materials.append(material)
    return o

def bevel(obj, width=0.03, segments=3):
    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    return mod

def smooth(obj):
    if obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True

# -----------------------------
# Character blockout
# -----------------------------
clear_scene()

uniform = mat("MAT_Uniform", (0.12, 0.14, 0.11), roughness=0.75)
gear = mat("MAT_Gear", (0.07, 0.08, 0.06), roughness=0.7)
skin = mat("MAT_Skin", (0.38, 0.22, 0.15), roughness=0.55)
metal = mat("MAT_Metal", (0.08, 0.08, 0.08), metallic=0.65, roughness=0.35)

# Torso + pelvis
chest = add_primitive("Body_Chest", "cube", (0,0,1.38), (0.29,0.18,0.36), uniform)
bevel(chest, 0.08, 5)
pelvis = add_primitive("Body_Pelvis", "cube", (0,0,0.98), (0.24,0.16,0.19), uniform)
bevel(pelvis, 0.07, 5)

# Head + neck
neck = add_primitive("Body_Neck", "cylinder", (0,0,1.76), (0.09,0.09,0.10), skin)
head = add_primitive("Body_Head", "uvsphere", (0,0,1.93), (0.13,0.11,0.17), skin)
smooth(head)

# Arms in A-pose
for side, sx in (("L",-1),("R",1)):
    upper = add_primitive(f"Body_UpperArm_{side}", "cylinder", (0.39*sx,0,1.47), (0.085,0.085,0.30), uniform, rotation=(0,0,0.28*sx))
    fore = add_primitive(f"Body_Forearm_{side}", "cylinder", (0.61*sx,0,1.22), (0.075,0.075,0.29), uniform, rotation=(0,0,0.12*sx))
    hand = add_primitive(f"Body_Hand_{side}", "cube", (0.69*sx,0,0.99), (0.075,0.05,0.10), skin)
    bevel(hand, 0.025, 3)

# Legs
for side, sx in (("L",-1),("R",1)):
    thigh = add_primitive(f"Body_Thigh_{side}", "cylinder", (0.13*sx,0,0.61), (0.11,0.11,0.36), uniform)
    shin = add_primitive(f"Body_Shin_{side}", "cylinder", (0.13*sx,0,0.04), (0.095,0.095,0.31), uniform)
    boot = add_primitive(f"Gear_Boot_{side}", "cube", (0.13*sx,-0.045,-0.28), (0.12,0.19,0.095), gear)
    bevel(boot, 0.035, 3)

# Tactical vest
vest = add_primitive("Gear_PlateCarrier", "cube", (0,-0.01,1.40), (0.32,0.21,0.31), gear)
bevel(vest, 0.045, 3)

# Front pouches
for i, x in enumerate((-0.16, 0.0, 0.16)):
    pouch = add_primitive(f"Gear_MagPouch_{i+1}", "cube", (x,-0.23,1.26), (0.065,0.05,0.12), gear)
    bevel(pouch, 0.018, 2)

# Helmet shell + visor
helmet = add_primitive("Gear_Helmet", "uvsphere", (0,0,2.06), (0.16,0.145,0.11), gear)
helmet.scale.z = 0.8
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
smooth(helmet)
visor = add_primitive("Gear_Visor", "cube", (0,-0.125,1.99), (0.10,0.018,0.035), metal)
bevel(visor, 0.01, 2)

# Backpack
pack = add_primitive("Gear_Backpack", "cube", (0,0.22,1.38), (0.25,0.10,0.30), gear)
bevel(pack, 0.04, 3)

# Holster and side utility pouch
holster = add_primitive("Gear_Holster", "cube", (0.28,-0.03,0.90), (0.065,0.07,0.13), gear)
bevel(holster, 0.02, 2)
utility = add_primitive("Gear_UtilityPouch", "cube", (-0.28,-0.02,0.92), (0.08,0.07,0.10), gear)
bevel(utility, 0.02, 2)

# -----------------------------
# Basic humanoid armature
# -----------------------------
bpy.ops.object.armature_add(enter_editmode=True, location=(0,0,-0.31))
arm = bpy.context.object
arm.name = "Soldier_Rig"
arm.show_in_front = True
edit = arm.data.edit_bones
root = edit[0]
root.name = "Root"
root.head = (0,0,0)
root.tail = (0,0,0.25)

def bone(name, head, tail, parent=None):
    b = edit.new(name)
    b.head = head
    b.tail = tail
    if parent:
        b.parent = parent
        b.use_connect = False
    return b

hips = bone("Hips", (0,0,0.45), (0,0,0.95), root)
sp1 = bone("Spine", (0,0,0.95), (0,0,1.30), hips)
sp2 = bone("Chest", (0,0,1.30), (0,0,1.63), sp1)
neckb = bone("Neck", (0,0,1.63), (0,0,1.80), sp2)
headb = bone("Head", (0,0,1.80), (0,0,2.08), neckb)

for side, sx in (("L",-1),("R",1)):
    ua = bone(f"UpperArm_{side}", (0.10*sx,0,1.56), (0.42*sx,0,1.47), sp2)
    fa = bone(f"LowerArm_{side}", (0.42*sx,0,1.47), (0.64*sx,0,1.18), ua)
    bone(f"Hand_{side}", (0.64*sx,0,1.18), (0.72*sx,0,0.99), fa)
    thigh = bone(f"UpperLeg_{side}", (0.11*sx,0,0.91), (0.13*sx,0,0.43), hips)
    shin = bone(f"LowerLeg_{side}", (0.13*sx,0,0.43), (0.13*sx,0,-0.12), thigh)
    bone(f"Foot_{side}", (0.13*sx,0,-0.12), (0.13*sx,-0.18,-0.28), shin)

bpy.ops.object.mode_set(mode='OBJECT')

# Parent meshes to rig object for organization (not full skinning yet)
for obj in [o for o in bpy.context.scene.objects if o.type == 'MESH']:
    obj.parent = arm

# Export collection-friendly naming
for obj in bpy.context.scene.objects:
    obj.select_set(True)

# Save master blend
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)

# Export Unity-ready FBX
bpy.ops.export_scene.fbx(
    filepath=OUT_FBX,
    use_selection=False,
    object_types={'ARMATURE','MESH'},
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',
    bake_space_transform=False,
    add_leaf_bones=False,
    use_armature_deform_only=True,
    mesh_smooth_type='FACE',
    use_mesh_modifiers=True,
    bake_anim=False,
    axis_forward='-Z',
    axis_up='Y'
)

print("Created:", OUT_BLEND)
print("Exported:", OUT_FBX)
