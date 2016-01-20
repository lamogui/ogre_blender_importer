# ogre_blender_importer
Ogre files importer (.mesh/.skeleton/.material) blender addon

The objective of this project is to recode the c++ class from ogre:
Ogre::MeshSerializer, Ogre::SkeletonSerializer and Ogre::MaterialSerializer
as interface between binary Ogre files (.mesh, .skeleton and .material) and
blender.

#How to install
git clone this repo inside your ""script/addon" directory of your blender

#How to contribute
Go to https://bitbucket.org/sinbad/ogre/src
Translate the code of Ogre::MeshSerializer, Ogre::SkeletonSerializer and
Ogre::MaterialSerializer into python3 for blender (bpy).
