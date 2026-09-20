# DroneCall 3D Soldier Asset Pipeline

This repository includes a Blender Python soldier generator for building a clean tactical-operator blockout and exporting a Unity-ready FBX.

## Run

From the repository root:

```bash
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" \
  --background \
  --python BlenderTools/Soldier/build_soldier.py
```

Generated files:

```text
Exports/
├── Soldier_Master.blend
└── Soldier_GameReady.fbx
```

## Current stage

The script creates:
- A-pose tactical soldier blockout
- separate body and equipment meshes
- helmet, plate carrier, magazine pouches, backpack, holster and boots
- basic humanoid skeleton
- Blender master file
- Unity-oriented FBX export

The next quality stage is replacing the procedural body blockout with an MPFB-generated human while keeping this rig/export pipeline.
