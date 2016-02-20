
import math;

try:
    import bpy;
    import mathutils;
except ImportError:
    print("This file need to be run with blender");


class OgreBone:
    """
    A bone in a skeleton.
    @remarks
        See Skeleton for more information about the principles behind skeletal animation.
        This class is a node in the joint hierarchy. Mesh vertices also have assignments
        to bones to define how they move in relation to the skeleton.
    """
    def __init__(self, name, handle, creator, blender_bone):
        self.name = name;
        self.handle = handle;
        self.creator = creator;
        self.local_position = mathutils.Vector((0,0,0));
        self.local_rotation = mathutils.Quaternion((1,0,0,0));
        self.local_scale = mathutils.Vector((1,1,1));
        self.rotation = self.local_rotation;
        self.blender_bone = blender_bone;
        self.childs = [];
        self.parent = None;
        self.parent_offset_rotation = mathutils.Quaternion((1,0,0,0));

        self.blender_bone.use_inherit_rotation = True;
        self.blender_bone.use_inherit_scale = True;
        #self.blender_bone.use_local_location = True;



    def computeBlenderBone(self):
        #Switch to blender repere
        self.alpha = OgreBone.getRotation(mathutils.Vector((0,1,0)),self.local_position);

        if (self.parent is not None):
            self.parent.computeBlenderBone();
            self.rotation = self.parent.rotation * self.parent.local_rotation;
            self.blender_bone.head = self.parent.blender_bone.tail;
            self.blender_bone.tail = self.rotation * self.local_position + self.blender_bone.head;
            self.gamma = OgreBone.getRotation(self.local_position,mathutils.Vector((0,1,0)));
            self.gamma = OgreBone.getRotation(mathutils.Vector((1,0,0)),mathutils.Vector((0,1,0)));

            #self.parent_offset_rotation = self.gamma.inverted();# * self.alpha;
            #self.parent_offset_rotation = OgreBone.getRotation(mathutils.Vector((0,1,0)),self.local_position);
        else:
            self.blender_bone.head = mathutils.Vector((0,0,0));
            self.blender_bone.tail = self.local_position;
            self.parent_offset_rotation = mathutils.Quaternion((1,0,0,0));

        #print("Bone " + self.name + " head pos " + str(self.blender_bone.head) + " tail pos " + str(self.blender_bone.tail));
        #print("Bone " + self.name + " local pos " + str(self.local_position));


    def getRotation(from_dir, to_dir):
        v1 = from_dir.normalized();
        v2 = to_dir.normalized();
        d = v1.dot(v2);
        if (d >= 1):
            return mathutils.Quaternion((1,0,0,0));
        if (d < (0.000001 - 1.0)):
            axis = mathutils.Vector((1,0,0)).cross(v1);
            if (axis.length < (0.000001)):
                axis = mathutils.Vector((0,0,1)).cross(v1);
            axis.normalize();
            return mathutils.Quaternion(axis,math.pi);
        s = math.sqrt((1.0+d)*2.0);
        invs = 1.0/s;
        c = v1.cross(v2);
        q = mathutils.Quaternion((s*0.5, c.x*invs, c.y*invs, c.z*invs));
        q.normalize();
        return q;



    def addChild(self, child):
        assert(child.parent is None);
        child.parent = self;
        child.blender_bone.parent = self.blender_bone;
        child.blender_bone.use_connect = True;
        self.childs.append(child);
        child.computeBlenderBone();
