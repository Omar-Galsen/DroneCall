import bpy, math

# DroneCall MPFB walk-cycle starter.
# Uses common MakeHuman/MPFB bone-name aliases and refuses to guess if key bones are absent.

armatures=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"]
rig=next((o for o in armatures if o.name=="Human.rig"), armatures[0] if armatures else None)
if not rig:
    raise RuntimeError("No armature found. Open Exports/MPFB_Soldier.blend first.")

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

def bone(key,required=True):
    for n in aliases[key]:
        if n in rig.pose.bones:return rig.pose.bones[n]
    # conservative normalized fallback
    want=[n.lower().replace("_","").replace(".","") for n in aliases[key]]
    for b in rig.pose.bones:
        x=b.name.lower().replace("_","").replace(".","")
        if x in want:return b
    if required: raise RuntimeError(f"Could not identify {key}. Available bones: "+", ".join(b.name for b in rig.pose.bones))
    return None

B={k:bone(k, k not in ("l_fore","r_fore")) for k in aliases}

# Create a clean reusable Blender Action.
action=bpy.data.actions.get("DC_Walk") or bpy.data.actions.new("DC_Walk")
rig.animation_data_create()
rig.animation_data.action=action

# Clear prior animation on these pose bones.
for pb in B.values():
    if pb:
        pb.rotation_mode="XYZ"
        pb.rotation_euler=(0,0,0)

def keyrot(pb,frame,x=0,y=0,z=0):
    if not pb:return
    pb.rotation_euler=(math.radians(x),math.radians(y),math.radians(z))
    pb.keyframe_insert("rotation_euler",frame=frame,group=pb.name)

# 25-frame seamless walk: contacts at 1/13/25, passing at 7/19.
poses=[
 (1,  28,-28, -10,10, -22,22, -8,8),
 (7,   0,  0,  28, 0,   0, 0, -18,4),
 (13,-28, 28,  10,-10, 22,-22, 8,-8),
 (19,  0,  0,   0,28,   0, 0, 4,-18),
 (25, 28,-28, -10,10, -22,22, -8,8),
]
for f,lt,rt,ls,rs,la,ra,lf,rf in poses:
    keyrot(B["l_thigh"],f,x=lt); keyrot(B["r_thigh"],f,x=rt)
    keyrot(B["l_shin"],f,x=ls); keyrot(B["r_shin"],f,x=rs)
    keyrot(B["l_arm"],f,x=la); keyrot(B["r_arm"],f,x=ra)
    keyrot(B["l_fore"],f,x=lf); keyrot(B["r_fore"],f,x=rf)
    # subtle hip counter-rotation
    keyrot(B["hips"],f,z=(2 if f in (1,25) else -2 if f==13 else 0))

# Linear interpolation gives a predictable first rig test.
if action:
    for fc in action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation="BEZIER"

scene=bpy.context.scene
scene.frame_start=1;scene.frame_end=24;scene.render.fps=24
scene.frame_set(1)
print("DC_Walk created on",rig.name,"frames 1-24")
