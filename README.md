# Ogre Blender Importer
Ogre files importer (.mesh/.skeleton/.material) blender addon

The objective of this project is to recode the c++ class from ogre:
Ogre::MeshSerializer, Ogre::SkeletonSerializer and Ogre::MaterialSerializer
as interface between binary Ogre files (.mesh, .skeleton and .material) and
blender.

## How to install

git clone this repo inside your "script/addon" directory of blender (in AppData or Program Files)

> git clone https://github.com/lamogui/ogre_blender_importer.git

then activate the addon in blender

> File > User Preferences > Add-ons > Ogre Blender Importer

## How to use
Note that is early dev code so number of features are missing.

Currently you can only load (.mesh) from the graphical interface and there is many limitations:
 - No materials are loaded or linked
 - No skeleton are loaded or linked
 - Mesh with multiple submesh crash
 - Only support version 1.10 of Ogre Mesh

Some experimental code is available to load .material and .skeleton see below

## Manual usage
You can to use addon "manually" using a terminal or powershell (so you need to add blender to PATH).

### Material (.material)
```
blender --python OgreMaterialSerializer.py -- file.material
```
Currently import simple things like Diffuse/Ambiant/Specular but also textures.
Textures are automatically loaded
No support at all for CYCLES

### Skeleton (.skeleton)
```
blender --python OgreSkeletonSerializer.py -- file.skeleton
```
Currently import armature only. For animations check the branch head_tail_experiment
for import animation (incorrectly).

### Mesh (.mesh)
```
blender --python OgreMeshSerializer.py -- file.mesh
```
Currently import mesh (only vertex positions and faces). No link with skeleton/materials.
One object is created per mesh (not submesh).

## How to contribute
Go to https://bitbucket.org/sinbad/ogre/src
Translate the code of Ogre::MeshSerializer, Ogre::SkeletonSerializerImpl and
Ogre::MaterialSerializer into python3 for blender (bpy).


### TODO
 * Correctly load animations (maths are buggy at the moment view head_tail_experiment branch)
 * Support scale import for bone
 * Import more .material parameters
 * Finnish the .mesh importer
 * Support older versions for .mesh and .Skeleton
 * Support Ogre2 Mesh and Skeletons
 * Mesh, Skeleton and Material exporters
