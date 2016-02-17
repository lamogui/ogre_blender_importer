# Ogre Blender Importer
Ogre files importer (.mesh/.skeleton/.material) blender addon

The objective of this project is to recode the c++ class from ogre:
Ogre::MeshSerializer, Ogre::SkeletonSerializer and Ogre::MaterialSerializer
as interface between binary Ogre files (.mesh, .skeleton and .material) and
blender.

#How to install
git clone this repo inside your ""script/addon" directory of blender (in AppData or Program Files)

#How to use
Currently only the .material and .skeleton import is working.
You can import one .material into blender using
```
blender --background --python OgreMaterialSerializer.py -- file.material
```

Same for .skeleton
```
blender --background --python OgreSkeletonSerializer.py -- file.skeleton
```


#How to contribute
Go to https://bitbucket.org/sinbad/ogre/src
Translate the code of Ogre::MeshSerializer, Ogre::SkeletonSerializer and
Ogre::MaterialSerializer into python3 for blender (bpy).
