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



    def isDefaultScale(self, vec3):
        assert(len(vec3) == 3)
        for v in vec3:
            if (v>1.0+self.epsilon or v <1.0-self.epsilon):
                return False;
        return True;

    def isNullVector(self, vec3):
        assert(len(vec3) == 3)
        for v in vec3:
            if (v > self.epsilon or v <-self.epsilon):
                return False;
        return True;

    def __init__(self):
        OgreSerializer.__init__(self);
        self._version = "[Unknown]";
        self.invertYZ = True;
        self.not_imported_bone_scales = {};
        self.not_imported_animation_translations = set();
        self.epsilon = 0.001;
        self.framerate = 60.0; #import animation at 60 fps
        self._ogreBoneMap = {}; #Handle to OgreBone
        self._animationBoneMap = {}; #OgreBone names to Real blender bones to animate
        self._nameHandleMap = {} #name to handle


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

    def _calcKeyFrameSizeWithoutScale(self, skeleton, keyframe):
        size = OgreSkeletonSerializer.SSTREAM_OVERHEAD_SIZE;
        size += 4; #time
        size += 4*4; #quaternion rotate
        size += 4*3; #translation
        return size;

    def _readBone(self,stream, skeleton):
        name = OgreSerializer.readString(stream);
        handle = self._readUShorts(stream,1)[0];

        bpy_bone = skeleton.edit_bones.new(name);
        bone = OgreBone(name, handle, skeleton, bpy_bone);

        self._ogreBoneMap[handle] = bone;
        self._nameHandleMap[name] = handle;

        bone.local_position = mathutils.Vector(self._readVector3(stream));
        bone.local_rotation = mathutils.Quaternion(self._readBlenderQuaternion(stream));

        self._chunkSizeStack[-1] += OgreSerializer.calcStringSize(name);

        #hum some ugly code <3
        if (self._currentstreamLen > self._calcBoneSizeWithoutScale(skeleton,bone)):
            scale = self._readVector3(stream);
            bone.local_scale = mathutils.Vector(scale);
            if (not self.isDefaultScale(scale)):
                self.not_imported_bone_scales[name] = bone.local_scale;

        print("Add Bone (handle: " + str(handle) + "): " + str(name));
        #print("pos: "+str(bone.local_position)+" rot: "+str(bone.local_rotation)+" scale:"+str(bone.local_scale));


    def _readBoneParent(self, stream, skeleton):
        childHandle = self._readUShorts(stream,1)[0];
        parentHandle = self._readUShorts(stream,1)[0];

        try:
            parent = self._ogreBoneMap[parentHandle];
            child = self._ogreBoneMap[childHandle];
            parent.addChild(child);
            #print("Create bone link [parent: " + parent.name + " (handle: "+str(parentHandle)+ "), child: " + child.name +" (handle:"+str(childHandle)+")]" );
        except IndexError as e:
            print(str(e) + " Attempt to create link for bone that doesn't exists");


    def _readKeyFrame(self, stream, tracks,skeleton ,anim, q):
        time = self._readFloats(stream, 1)[0] * self.framerate;

        #Add rotation/scale necessary

        for i in range(3,10):
            for t in tracks:
                t[i].keyframe_points.add(1);
                t[i].keyframe_points[-1].interpolation = 'LINEAR';


        rot = mathutils.Quaternion(self._readBlenderQuaternion(stream));
        trans = self._readVector3(stream);

        if (not self.isNullVector(trans)):
            if (anim.name not in self.not_imported_animation_translations):
                self.not_imported_animation_translations.add(anim.name);

        for index,t in enumerate(tracks):
            #position
            #t[0].keyframe_points[-1].co = (time, trans[0]);
            #t[1].keyframe_points[-1].co = (time, trans[1]);
            #t[2].keyframe_points[-1].co = (time, trans[2]);

            #rotation
            crot = rot * q[index];
            t[3].keyframe_points[-1].co = (time , crot.w);
            t[4].keyframe_points[-1].co = (time , crot.x);
            t[5].keyframe_points[-1].co = (time , crot.y);
            t[6].keyframe_points[-1].co = (time , crot.z);


        #hum ugly again <3
        if (self._currentstreamLen > self._calcKeyFrameSizeWithoutScale(skeleton,tracks)):
            scale = self._readVector3(stream);
            for t in tracks:
                t[7].keyframe_points[-1].co = (time, scale[0]);
                t[8].keyframe_points[-1].co = (time, scale[1]);
                t[9].keyframe_points[-1].co = (time, scale[2]);
        else:
            for t in tracks:
                t[7].keyframe_points[-1].co = (time, 1.0);
                t[8].keyframe_points[-1].co = (time, 1.0);
                t[9].keyframe_points[-1].co = (time, 1.0);


    def _readAnimationTrack(self,stream,skeleton,anim):
        boneHandle = self._readShorts(stream,1)[0];
        targetAnimationBones = [];
        try:
            targetOgreBone = self._ogreBoneMap[boneHandle];
            targetAnimationBones = self._animationBoneMap[targetOgreBone.name];
        except IndexError as e:
            print("Attempt to create an animation track for a bone that doesn't exists (bone handle: " + str(boneHandle) + ")");


        tracks = [];
        offset_quaternion = []
        for b in targetAnimationBones:
            #Creates curves for the animations of a boneHandle
            # 0: position.x
            # 1: position.y
            # 2: position.z
            # 3: rotation.w
            # 4: rotation.x
            # 5: rotation.y
            # 6: rotation.z
            # 7: scale.x
            # 8: scale.y
            # 9: scale.z
            t = []
            basename = 'pose.bones["' + b.name + '"]';
            #t.append(anim.fcurves.new(data_path=basename+".location",index=0,action_group=b.name));
            #t.append(anim.fcurves.new(data_path=basename+".location",index=1,action_group=b.name));
            #t.append(anim.fcurves.new(data_path=basename+".location",index=2,action_group=b.name));
            t.append(None); #Don't support "robotic" armatures (with translations) yet
            t.append(None);
            t.append(None);
            t.append(anim.fcurves.new(data_path=basename+".rotation_quaternion",index=0,action_group=b.name));
            t.append(anim.fcurves.new(data_path=basename+".rotation_quaternion",index=1,action_group=b.name));
            t.append(anim.fcurves.new(data_path=basename+".rotation_quaternion",index=2,action_group=b.name));
            t.append(anim.fcurves.new(data_path=basename+".rotation_quaternion",index=3,action_group=b.name));
            t.append(anim.fcurves.new(data_path=basename+".scale",index=0,action_group=b.name));
            t.append(anim.fcurves.new(data_path=basename+".scale",index=1,action_group=b.name));
            t.append(anim.fcurves.new(data_path=basename+".scale",index=2,action_group=b.name));
            tracks.append(t);
            offset_quaternion.append(self._ogreBoneMap[self._nameHandleMap[b.name]].parent_offset_rotation);

        self._pushInnerChunk(stream);
        streamID = self._readChunk(stream);
        while (streamID == OgreSkeletonChunkID.SKELETON_ANIMATION_TRACK_KEYFRAME):
            self._readKeyFrame(stream, tracks, skeleton, anim, offset_quaternion);
            streamID = self._readChunk(stream);
        if (streamID is not None):
            self._backpedalChunkHeader(stream);
        self._popInnerChunk(stream);




    def _readAnimation(self, stream, skeleton, skeleton_object):
        self._createAnimationBoneMap(skeleton);

        #name of the animation
        name = OgreSerializer.readString(stream);
        #length of the animation in seconds
        length = self._readFloats(stream, 1)[0];

        print("Creating action: " + name + " (length: " + str(length) + "s)");

        pAnim = bpy.data.actions.new(name);
        skeleton_object.animation_data.action = pAnim;
        eof = False;

        self._pushInnerChunk(stream);
        streamID = self._readChunk(stream);

        if (streamID == OgreSkeletonChunkID.SKELETON_ANIMATION_BASEINFO):
            baseAnimName = OgreSkeletonSerializer.readString(stream);
            baseKeyTime = self._readFloats(stream,1)[0];
            print("This animation is based on: "+baseAnimName+" (with the key time: +"+str(baseKeyTime)+")");
            print("Warning this is not implemented yet");
            #TODO code the base key frame implementation
            streamID = self._readChunk(stream);

        while (streamID==OgreSkeletonChunkID.SKELETON_ANIMATION_TRACK):
            self._readAnimationTrack(stream, skeleton, pAnim);
            streamID = self._readChunk(stream);

        if (stream is not None):
            self._backpedalChunkHeader(stream);
        self._popInnerChunk(stream);





    def setWorkingVersion(self, ver):
        if (ver == OgreSkeletonVersion.SKELETON_VERSION_1_0):
            self._version = "[Serializer_v1.10]";
        elif (ver == OgreSkeletonVersion.SKELETON_VERSION_1_8):
            self._version = "[Serializer_v1.80]";
        else:
            raise ValueError("Invalid Skeleton serializer version " + str(ver));

    #grab the correct bones to animate when ogre call for the bone name
    def getAnimationBones(ogrebone, armature):
        for bone in armature.bones:
            #The bone exists so grabs his childrens
            if (bone.name == ogrebone.name):
                return bone.children;
        #the bone has been removed due to its 0 length
        realbones = [];
        for child in ogrebone.childs:
            for bone in armature.bones:
                if (bone.name == child.name):
                    realbones.append(bone);
        return realbones;


    def _createAnimationBoneMap(self,armature):
        self._animationBoneMap = {}
        for ogrebone in self._ogreBoneMap.values():
            self._animationBoneMap[ogrebone.name] = OgreSkeletonSerializer.getAnimationBones(ogrebone,armature);


    def importSkeleton(self, stream, filename=None):
        if (filename is None):
            if (hasattr(stream,'name')):
                filename = stream.name;
            elif (hasattr(stream, 'filename')):
                filename = stream.filename;
            else:
                raise ValueError("Cannot determine the filename of the stream please add filename parameter")

        self._ogreBoneMap = {};
        self._nameHandleMap = {};
        self._animationBoneMap = {};
        self.not_imported_bone_scales = {};
        self.not_imported_animation_translations = set();
        self._determineEndianness(stream);
        self._readFileHeader(stream);
        self._pushInnerChunk(stream);

        filename = os.path.basename(filename);
        skeleton_name = os.path.splitext(filename)[0];

        skeleton = None;
        skeleton_object = None;


        if skeleton_name in bpy.data.armatures.keys():
            raise ValueError(skeleton_name + " already exists in blender");

        print("Create armature from skeleton: " + skeleton_name);
        skeleton = bpy.data.armatures.new(skeleton_name);
        #to be able to edit the armature we need to got in edit mode.
        skeleton_object = bpy.data.objects.new(skeleton_name, skeleton);
        #skeleton_object.show_x_ray = True;
        skeleton_object.animation_data_create();
        scene = bpy.context.scene;
        scene.objects.link(skeleton_object);
        scene.objects.active=skeleton_object;
        scene.update();
        scene.objects.active=skeleton_object;

        skeleton.show_names = True;

        streamID = self._readChunk(stream);
        while (streamID is not None):
            if (streamID==OgreSkeletonChunkID.SKELETON_BLENDMODE):
                blendMode = self._readUShorts(stream,1)[0];
                print("Find blendMode: " + str(blendMode) + " (not used)");
            elif (streamID==OgreSkeletonChunkID.SKELETON_BONE):
                assert(bpy.ops.object.mode_set(mode='EDIT')=={'FINISHED'});
                self._readBone(stream, skeleton);
            elif (streamID==OgreSkeletonChunkID.SKELETON_BONE_PARENT):
                assert(bpy.ops.object.mode_set(mode='EDIT')=={'FINISHED'});
                self._readBoneParent(stream, skeleton);
            elif (streamID==OgreSkeletonChunkID.SKELETON_ANIMATION):
                assert(bpy.ops.object.mode_set(mode='OBJECT')=={'FINISHED'});
                self._readAnimation(stream,skeleton, skeleton_object);
            elif (streamID==OgreSkeletonChunkID.SKELETON_ANIMATION_LINK):
                assert(bpy.ops.object.mode_set(mode='OBJECT')=={'FINISHED'});
                self._readSkeletonAnimationLink(stream,skeleton);

            streamID=self._readChunk(stream);
        #TODO skeleton set binding possible
        self._popInnerChunk(stream);
        if (len(self.not_imported_bone_scales)>0):
            print("Warning: scale import for bones is not supported yet (" + str(len(self.not_imported_bone_scales)) + " bones may have incorrectly loaded):");
            #print(str(self.not_imported_bone_scales));
        if (len(self.not_imported_animation_translations)>0):
            print("Warning: translation import for animations is not supported yet (" + str(len(self.not_imported_animation_translations)) + " animations may have incorrectly loaded)");
            #print(str(self.not_imported_animation_translations));



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
