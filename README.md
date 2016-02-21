# Ogre Blender Importer
Ogre files importer (.mesh/.skeleton/.material) blender addon

The objective of this project is to recode the c++ class from ogre:
Ogre::MeshSerializer, Ogre::SkeletonSerializer and Ogre::MaterialSerializer
as interface between binary Ogre files (.mesh, .skeleton and .material) and
blender.

##How to install
git clone this repo inside your ""script/addon" directory of blender (in AppData or Program Files)

##How to use
Currently you need to use addon "manually" using a terminal or powershell (so you need to add blender to PATH).
Note that is early dev code so number of feature are missing.


###Material (.material)
```
blender --python OgreMaterialSerializer.py -- file.material
```
Currently import simple things like Diffuse/Ambiant/Specular but also textures.
Textures are automatically loaded

###Skeleton (.skeleton)
```
blender --python OgreSkeletonSerializer.py -- file.skeleton
```
Currently import armature only. For animations check the branch head_tail_experiment
for import animation (incorrectly).

###Mesh (.mesh)
```
blender --python OgreMeshSerializer.py -- file.mesh
```
Currently import nothing, but capable of reading some files entirely


##How to contribute
Go to https://bitbucket.org/sinbad/ogre/src
Translate the code of Ogre::MeshSerializer, Ogre::SkeletonSerializer and
Ogre::MaterialSerializer into python3 for blender (bpy).


###TODO
 * Correctly load animations (maths are buggy at the moment view head_tail_experiment branch)
 * Support scale import for bone
 * Import more .material parameters
 * Finnish the .mesh importer
 * Support older versions for .mesh and .Skeleton
 * Support Ogre2 Mesh and Skeletons
 * Mesh, Skeleton and Material exporters
