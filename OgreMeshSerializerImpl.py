from OgreSerializer import OgreSerializer
from OgreMeshFileFormat import *


class OgreMeshSerializerImpl(OgreSerializer):
    """
    Internal implementation of Mesh reading / writing for the latest version of the
    .mesh format.
    @remarks
    In order to maintain compatibility with older versions of the .mesh format, there
    will be alternative subclasses of this class to load older versions, whilst this class
    will remain to load the latest version.

     @note
        This mesh format was used from Ogre v1.10.

    from: OgreMain/OgreMeshSerializerImpl.h
    url: https://bitbucket.org/sinbad/ogre/src/0d580c7216abe27fafe41cb43e31d8ed86ded591/OgreMain/include/OgreMeshSerializerImpl.h
    """

    MSTREAM_OVERHEAD_SIZE = 2 + 4;

    def __init__(self):
        OgreSerializer.__init__(self);
        self._version = "[MeshSerializer_v1.100]";

    #def _readGeometry(self, stream, mesh):


    def _readMesh(self, stream, mesh, listener):
        skeletallyAnimated = self._readBools(stream,1)[0];
        eof = False;

        while (not eof):
            self._pushInnerChunk(stream);
            try:
                streamID = self._readChunk(stream);
            except EOFError as e:
                eof = True;
            while (not eof and \
                  (streamID == OgreMeshChunkID.M_GEOMETRY or \
                   streamID == OgreMeshChunkID.M_SUBMESH or \
                   streamID == OgreMeshChunkID.M_MESH_SKELETON_LINK or \
                   streamID == OgreMeshChunkID.M_MESH_BONE_ASSIGNMENT or \
                   streamID == OgreMeshChunkID.M_MESH_LOD_LEVEL or \
                   streamID == OgreMeshChunkID.M_MESH_BOUNDS or \
                   streamID == OgreMeshChunkID.M_SUBMESH_NAME_TABLE or \
                   streamID == OgreMeshChunkID.M_EDGE_LISTS or \
                   streamID == OgreMeshChunkID.M_POSES or \
                   streamID == OgreMeshChunkID.M_ANIMATIONS or \
                   streamID == M_TABLE_EXTREMES)):
                if (streamID==OgreMeshChunkID.M_GEOMETRY):
                    self._readGeometry(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_SUBMESH):
                    self._readSubMesh(stream,mesh,listener);
                elif (streamID==OgreMeshChunkID.M_MESH_SKELETON_LINK):
                    self._readSkeletonLink(stream,mesh,listener);
                elif (streamID==OgreMeshChunkID.M_MESH_BONE_ASSIGNMENT):
                    self._readMeshBoneAssignment(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_MESH_LOD_LEVEL):
                    self._readMeshLodLevel(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_MESH_BOUNDS):
                    self._readBoundsInfos(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_SUBMESH_NAME_TABLE):
                    self._readSubMeshNameTable(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_EDGE_LISTS):
                    self._readEdgeList(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_POSES):
                    self._readPoses(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_ANIMATIONS):
                    self._readAnimations(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_TABLE_EXTREMES):
                    self._readExtremes(stream,mesh);

                try:
                    streamID == self._readChunk(stream);
                except EOFError as e:
                    eof = True;

            if (not eof):
                self._backpedalChunkHeader(stream);
            self._popInnerChunk(stream);





    def importMesh(self, stream, mesh, listener=None):
        self._determineEndianness(stream);
        self._readFileHeader(stream);
        self._pushInnerChunk(stream);
        streamID = self._readChunk(stream);

        eof = False;
        while (not eof):
            if (streamID == OgreMeshChunkID.M_MESH):
                self._readMesh(stream, mesh, listener);
            try:
                streamID = self._readChunk(stream);
            except EOFError as e:
                print("Legit end of file (no more chunks) at " + str(stream.tell()) + " exception message:" + e.message);
                eof = True;
