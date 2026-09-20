import bpy
import math

# DroneCall modular tactical helmet.
# Builds a standalone high-cut helmet at the 3D cursor.
# This is intentionally independent of the soldier so it can be inspected/refined first.

COL = "TAC_Helmet_Component"

def mat(name, color, metallic=0.0, rough=0.55):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metallic
    p.inputs["Roughness"].default_value=rough
    return m

def collection():
    old=bpy.data.collections.get(COL)
    if old:
        for o in list(old.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(old)
    c=bpy.data.collections.new(COL)
    bpy.context.scene.collection.children.link(c)
    return c

def move(o,c):
    for x in list(o.users_collection): x.objects.unlink(o)
    c.objects.link(o)

def bevel(o,w=.006,n=3):
    b=o.modifiers.new("EdgeBevel","BEVEL"); b.width=w; b.segments=n

def cube(name,loc,scale,material,rot=(0,0,0),bev=.006):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=rot)
    o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bevel(o,bev);o.data.materials.append(material);move(o,C);return o

C=collection()
shellmat=mat("Helmet_Olive",(0.10,.115,.075),0,.62)
railmat=mat("Helmet_Rail",(0.025,.028,.025),.15,.42)
metal=mat("Helmet_Metal",(.035,.038,.035),.65,.32)
rubber=mat("Helmet_Rubber",(.018,.02,.018),0,.78)

origin=bpy.context.scene.cursor.location.copy()
x,y,z=origin

# Main shell: UV sphere cut to a high-cut helmet silhouette.
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, location=(x,y,z+.05))
shell=bpy.context.object;shell.name="Helmet_Shell"
shell.scale=(.155,.175,.135)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)

# remove lower vertices for high-cut shape
bpy.context.view_layer.objects.active=shell
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
for v in shell.data.vertices:
    # local shell coordinates; trim bottom and open ear regions
    if v.co.z < -.025:
        v.select=True
    if v.co.z < .015 and abs(v.co.x) > .105:
        v.select=True
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.delete(type='VERT')
bpy.ops.object.mode_set(mode='OBJECT')

solid=shell.modifiers.new("ShellThickness","SOLIDIFY");solid.thickness=.006
bev=shell.modifiers.new("ShellEdgeSoftness","BEVEL");bev.width=.003;bev.segments=2
for p in shell.data.polygons:p.use_smooth=True
shell.data.materials.append(shellmat);move(shell,C)

# Front brow / lower rim
cube("Helmet_FrontRim",(x,y-.151,z+.015),(.105,.012,.018),shellmat,bev=.008)

# ARC-style side rails
for s in (-1,1):
    cube(f"Helmet_SideRail_{'L' if s<0 else 'R'}",
         (x+s*.137,y-.005,z+.025),(.012,.098,.027),railmat,
         rot=(0,0,s*math.radians(4)),bev=.008)
    # rail slots
    for i,yy in enumerate((-.05,0,.05)):
        cube(f"Helmet_RailSlot_{s}_{i}",
             (x+s*.151,y+yy,z+.025),(.006,.018,.007),metal,bev=.003)

# NVG shroud: central plate + three anchor points
cube("Helmet_NVG_Shroud",(x,y-.177,z+.062),(.046,.009,.038),railmat,bev=.007)
cube("Helmet_NVG_Center",(x,y-.190,z+.062),(.018,.009,.018),metal,bev=.004)
for s in (-1,1):
    cube(f"Helmet_NVG_Anchor_{s}",(x+s*.035,y-.184,z+.042),(.009,.008,.009),metal,bev=.003)

# Velcro / patch panels
cube("Helmet_Velcro_Top",(x,y-.015,z+.178),(.055,.065,.003),rubber,bev=.008)
for s in (-1,1):
    cube(f"Helmet_Velcro_Side_{s}",(x+s*.105,y-.045,z+.095),(.035,.045,.003),rubber,
         rot=(0,math.radians(72)*s,0),bev=.006)

# Rear retention block
cube("Helmet_RearRetention",(x,y+.158,z+.035),(.055,.014,.032),railmat,bev=.008)

# Side accessory mounts
for s in (-1,1):
    cube(f"Helmet_AccessoryMount_{s}",(x+s*.155,y-.055,z+.025),(.014,.025,.021),metal,bev=.004)

# Simple chin strap anchors (visual component, not rigged yet)
for s in (-1,1):
    cube(f"Helmet_StrapAnchor_{s}",(x+s*.125,y+.06,z-.005),(.012,.012,.018),rubber,
         rot=(0,0,s*math.radians(12)),bev=.004)

# metadata
for o in C.objects:
    o["dronecall_component"]="helmet"
    o["modular_asset"]=True

# select helmet component
bpy.ops.object.select_all(action='DESELECT')
for o in C.objects:o.select_set(True)

print("DroneCall helmet created.")
print("Component objects:",len(C.objects))
