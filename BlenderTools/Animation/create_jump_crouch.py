import bpy, math

# DroneCall: create jump and crouch actions for the MPFB Human.rig.
rig=bpy.data.objects.get("Human.rig")
if not rig or rig.type!="ARMATURE":
    raise RuntimeError("Human.rig not found. Open Exports/MPFB_Soldier.blend first.")

aliases={
 "hips":["pelvis","hips","root"],
 "l_thigh":["thigh.L","upperleg01.L","upperleg_l","LeftUpLeg"],
 "r_thigh":["thigh.R","upperleg01.R","upperleg_r","RightUpLeg"],
 "l_shin":["shin.L","lowerleg01.L","lowerleg_l","LeftLeg"],
 "r_shin":["shin.R","lowerleg01.R","lowerleg_r","RightLeg"],
 "l_arm":["upper_arm.L","upperarm01.L","upperarm_l","LeftArm"],
 "r_arm":["upper_arm.R","upperarm01.R","upperarm_r","RightArm"],
 "l_fore":["forearm.L","lowerarm01.L","lowerarm_l","LeftForeArm"],
 "r_fore":["forearm.R","lowerarm01.R","lowerarm_r","RightForeArm"],
}

def bone(key):
    for n in aliases[key]:
        if n in rig.pose.bones:return rig.pose.bones[n]
    raise RuntimeError("Missing bone "+key+". Available: "+", ".join(b.name for b in rig.pose.bones))

B={k:bone(k) for k in aliases}

def reset():
    for p in B.values():
        p.rotation_mode="XYZ";p.rotation_euler=(0,0,0);p.location=(0,0,0)

def rot(p,f,x=0,y=0,z=0):
    p.rotation_euler=(math.radians(x),math.radians(y),math.radians(z))
    p.keyframe_insert("rotation_euler",frame=f,group=p.name)

def loc(p,f,x=0,y=0,z=0):
    p.location=(x,y,z);p.keyframe_insert("location",frame=f,group=p.name)

def new_action(name):
    a=bpy.data.actions.get(name)
    if a:bpy.data.actions.remove(a)
    a=bpy.data.actions.new(name);rig.animation_data_create();rig.animation_data.action=a;reset();return a

# CROUCH: standing -> descend -> hold crouch.
a=new_action("DC_Crouch")
for f,t,s,arm,hipz in [(1,0,0,0,0),(8,32,62,-8,-.18),(14,48,88,-12,-.30),(24,48,88,-12,-.30)]:
    rot(B["l_thigh"],f,x=t);rot(B["r_thigh"],f,x=t)
    rot(B["l_shin"],f,x=-s);rot(B["r_shin"],f,x=-s)
    rot(B["l_arm"],f,x=arm);rot(B["r_arm"],f,x=arm)
    rot(B["l_fore"],f,x=-15);rot(B["r_fore"],f,x=-15)
    loc(B["hips"],f,z=hipz)
for fc in a.fcurves:
    for k in fc.keyframe_points:k.interpolation="BEZIER"

# JUMP: anticipation -> takeoff -> apex -> landing -> recover.
a=new_action("DC_Jump")
jump=[
 (1,  0,  0,  0, 0.00),
 (5, 28,-55, 15,-.12),
 (9,-18,-25,-28, .12),
 (13,-25,-35,-38, .30),
 (17,-12,-30,-22, .16),
 (21,30,-60, 18,-.10),
 (26, 0,  0,  0, 0.00),
]
for f,t,s,arm,hipz in jump:
    rot(B["l_thigh"],f,x=t);rot(B["r_thigh"],f,x=t)
    rot(B["l_shin"],f,x=s);rot(B["r_shin"],f,x=s)
    rot(B["l_arm"],f,x=arm);rot(B["r_arm"],f,x=arm)
    rot(B["l_fore"],f,x=-18);rot(B["r_fore"],f,x=-18)
    loc(B["hips"],f,z=hipz)
for fc in a.fcurves:
    for k in fc.keyframe_points:k.interpolation="BEZIER"

# Leave jump active for immediate preview.
rig.animation_data.action=bpy.data.actions["DC_Jump"]
scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=26;scene.render.fps=24;scene.frame_set(1)
print("Created DC_Jump and DC_Crouch. DC_Jump is active.")
