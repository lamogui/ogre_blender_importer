from enum import Enum
from io import open
import os

try:
    import bpy;
except ImportError:
    print("You need to execute this script using blender");
    print("usage: blender --background --python OgreSkeletonSerializer.py -- file.skeleton");

try:
    from OgreSkeletonFileFormat import OgreSkeletonChunkID
    from OgreSerializer import OgreSerializer

except ImportError as e:
    print("Import error: " + str(e) + " manual compilation" );
    srcfile="OgreSkeletonFileFormat.py"; exec(compile(open(srcfile).read(), srcfile, 'exec'))
    srcfile="OgreSerializer.py"; exec(compile(open(srcfile).read(), srcfile, 'exec'))

class OgreSkeletonVersion(Enum):
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

    def _readBone(self,stream, skeleton):
        name = self.readString(stream);
        handle = self._readUShorts(stream,1)[0];
        bone = skeleton.edit_bones.new(name);
        pos = self._readVector3(stream);
        q = self._readQuaternion(stream);

        self._chunkSizeStack[-1] += OgreSerializer.calcStringSize(name);

        #hum some ugly code <3
        scale = (1.0,1.0,1.0);
        if (self._currentstreamLen > self._calcBoneSizeWithoutScale(skeleton,bone)):
            scale = self._readVector3(stream);




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
        skeleton_name = os.path.splitext(filename);

        if skeleton_name in bpy.data.armatures.keys():
            raise ValueError(skeleton_name + " already exists in blender");
        else:
            skeleton_name = bpy.data.armatures.new(name=skeleton_name);

        streamID = self._readChunk(stream);
        while (streamID is not None):
            if (streamID==OgreSkeletonChunkID.SKELETON_BLENDMODE):
                blendMode = self._readUShorts(stream,1)[0];
                print("Find blendMode: " + str(blendMode) + " (not used)");
            elif (streamID==OgreSkeletonChunkID.SKELETON_BONE):
                self._readBone(stream, skeleton);
            elif (streamID==OgreSkeletonChunkID.SKELETON_BONE_PARENT):
                self._readBoneParent(stream, skeleton);
            elif (streamID==OgreSkeletonChunkID.SKELETON_ANIMATION):
                self._readAnimation(stream,skeleton);
            elif (streamID==OgreSkeletonChunkID.SKELETON_ANIMATION_LINK):
                self._readSkeletonAnimationLink(stream,skeleton);

            streamID=self._readChunk(stream);
        #TODO skeleton set binding possible
        self._popInnerChunk(stream);
