from enum import Enum
from io import open
import os

try:
    import bpy;
    import mathutils;
except ImportError:
    print("You need to execute this script using blender");
    print("usage: blender --background --python OgreSkeletonSerializer.py -- file.skeleton");

try:
    from OgreSkeletonFileFormat import OgreSkeletonChunkID
    from OgreSerializer import OgreSerializer
    from OgreBone import OgreBone

except ImportError as e:
    print("Import error: " + str(e) + " manual compilation" );
    srcfile="OgreSkeletonFileFormat.py"; exec(compile(open(srcfile).read(), srcfile, 'exec'))
    srcfile="OgreSerializer.py"; exec(compile(open(srcfile).read(), srcfile, 'exec'))
    srcfile="OgreBone.py"; exec(compile(open(srcfile).read(), srcfile, 'exec'))

class OgreSkeletonVersion(IntEnum):
    #/// OGRE version v1.0+
    SKELETON_VERSION_1_0 = 100;
    #/// OGRE version v1.8+
    SKELETON_VERSION_1_8 = 180;
    #Latest version available
    SKELETON_VERSION_LATEST = 180;

class OgreSkeletonSerializer(OgreSerializer):
    """
    Class for serialising skeleton data to/from an OGRE .skeleton file.
    @remarks
        This class allows exporters to write OGRE .skeleton files easily, and allows the
        OGRE engine to import .skeleton files into instantiated OGRE Skeleton objects.
        Note that a .skeleton file includes not only the Skeleton, but also definitions of
        any Animations it uses.
    @par
        To export a Skeleton:<OL>
        <LI>Create a Skeleton object and populate it using it's methods.</LI>
        <LI>Call the exportSkeleton method</LI>
        </OL>
    """

    SSTREAM_OVERHEAD_SIZE = 2 + 4;
    HEADER_STREAM_ID_EXT = 0x1000;

    def __init__(self):
        OgreSerializer.__init__(self);
        self._version = "[Unknown]";

    def _calcBoneSizeWithoutScale(self, skeleton, bone):
        size = OgreSkeletonSerializer.SSTREAM_OVERHEAD_SIZE;
        size += 2; #handle
        size += 4*3; #position
        size += 4*4; #orientation
        return size;

    def _calcBoneSize(self, skeleton, bone):
        size = self._calcBoneSizeWithoutScale(skeleton,bone);
        #TODO Don't assume the scale it's never unit scale
        size += 3*3; #scale
        return size;

    def _readBone(self,stream, skeleton, bone_map):
        name = OgreSerializer.readString(stream);
        handle = self._readUShorts(stream,1)[0];

        bpy_bone = skeleton.edit_bones.new(name);

        bone = OgreBone(name, handle, skeleton, bpy_bone, bone_map);
        bone_map[handle] = bone;

        bone.position = mathutils.Vector(self._readVector3(stream));
        bone.rotation = mathutils.Quaternion(self._readQuaternion(stream));

        self._chunkSizeStack[-1] += OgreSerializer.calcStringSize(name);

        #hum some ugly code <3
        if (self._currentstreamLen > self._calcBoneSizeWithoutScale(skeleton,bone)):
            bone.scale = mathutils.Vector(self._readVector3(stream));

        print("Add Bone (handle: " + str(handle) + "): " + str(name));
        print("pos: "+str(bone.position)+" rot: "+str(bone.rotation)+" scale:"+str(bone.scale));


    def _readBoneParent(self, stream, skeleton, bone_map):
        childHandle = self._readUShorts(stream,1)[0];
        parentHandle = self._readUShorts(stream,1)[0];

        try:
            parent = bone_map[parentHandle];
            child = bone_map[childHandle];
            parent.addChild(child);
            print("Create bone link [parent: " + parent.name + " (handle: "+str(parentHandle)+ "), child: " + child.name +" (handle:"+str(childHandle)+")]" );
        except IndexError as e:
            print(str(e) + " Attempt to create link for bone that doesn't exists");


    def setWorkingVersion(self, ver):
        if (ver == OgreSkeletonVersion.SKELETON_VERSION_1_0):
            self._version = "[Serializer_v1.10]";
        elif (ver == OgreSkeletonVersion.SKELETON_VERSION_1_8):
            self._version = "[Serializer_v1.80]";
        else:
            raise ValueError("Invalid Skeleton serializer version " + str(ver));

    def importSkeleton(self, stream, filename=None):
        if (filename is None):
            if (hasattr(stream,'name')):
                filename = stream.name;
            elif (hasattr(stream, 'filename')):
                filename = stream.filename;
            else:
                raise ValueError("Cannot determine the filename of the stream please add filename parameter")

        self._determineEndianness(stream);
        self._readFileHeader(stream);
        self._pushInnerChunk(stream);

        filename = os.path.basename(filename);
        skeleton_name = os.path.splitext(filename)[0];

        skeleton = None;
        skeleton_object = None;


        if skeleton_name in bpy.data.armatures.keys():
            raise ValueError(skeleton_name + " already exists in blender");
        else:
            print("Create armature from skeleton: " + skeleton_name);
            skeleton = bpy.data.armatures.new(skeleton_name);
            #to be able to edit the armature we need to got in edit mode.
            skeleton_object = bpy.data.objects.new(skeleton_name, skeleton);
            skeleton_object.show_x_ray = True;
            scene = bpy.context.scene;
            scene.objects.link(skeleton_object);
            scene.objects.active=skeleton_object;
            scene.update();
            #bugged ? bpy.ops.object.object.mode_set(mode='EDIT');
            bpy.ops.object.editmode_toggle();

        skeleton.show_names = True;
        bone_map = {};

        streamID = self._readChunk(stream);
        while (streamID is not None):
            if (streamID==OgreSkeletonChunkID.SKELETON_BLENDMODE):
                blendMode = self._readUShorts(stream,1)[0];
                print("Find blendMode: " + str(blendMode) + " (not used)");
            elif (streamID==OgreSkeletonChunkID.SKELETON_BONE):
                self._readBone(stream, skeleton, bone_map);
            elif (streamID==OgreSkeletonChunkID.SKELETON_BONE_PARENT):
                self._readBoneParent(stream, skeleton, bone_map);
            elif (streamID==OgreSkeletonChunkID.SKELETON_ANIMATION):
                self._readAnimation(stream,skeleton);
            elif (streamID==OgreSkeletonChunkID.SKELETON_ANIMATION_LINK):
                self._readSkeletonAnimationLink(stream,skeleton);

            streamID=self._readChunk(stream);
        #TODO skeleton set binding possible
        self._popInnerChunk(stream);

if __name__ == "__main__":
    argv = sys.argv;
    argv = argv[argv.index("--")+1:];  # get all args after "--"
    if (len(argv) > 0):
        filename = argv[0];
        skeletonfile = open(filename,mode='rb');
        skeletonserializer = OgreSkeletonSerializer();
        skeletonserializer.disableValidation();
        skeletonserializer.setWorkingVersion(OgreSkeletonVersion.SKELETON_VERSION_LATEST);
        skeletonserializer.importSkeleton(skeletonfile);
    else:
        print("usage: blender --background --python OgreSkeletonSerializer.py -- file.skeleton");
