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


    def _readGeometryVertexElement(self,stream,mesh):
        source = self._readUShorts(stream,1)[0];
        vType = self._readUShorts(stream,1)[0];
        vSemantic = self._readUShorts(stream, 1)[0];
        offset = self._readUShorts(stream, 1)[0];
        index = self._readUShorts(stream, 1)[0];
        print("source " + str(source) + " vType {0:#04x}".format(vType));
        print("vSemantic {0:#04x}".format(vSemantic).format(vSemantic));
        print("offset " + str(offset) + " index " + str(index));


    def _readGeometryVertexDeclaration(self,stream,mesh):
        self._pushInnerChunk(stream);
        streamID = None;
        eof = False;
        try:
            streamID = self._readChunk(stream);
            print("streamID " + "{0:#04x}".format(streamID) + " (offset: {0:#0x})".format(stream.tell()));
        except EOFError as e:
            eof = True;
        while (not eof and streamID == OgreMeshChunkID.M_GEOMETRY_VERTEX_ELEMENT):
            if (streamID == OgreMeshChunkID.M_GEOMETRY_VERTEX_ELEMENT):
                print("M_GEOMETRY_VERTEX_ELEMENT");
                self._readGeometryVertexElement(stream,mesh);
            try:
                streamID = self._readChunk(stream);
                print("streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
            except EOFError as e:
                eof = True;
        if (not eof):
            self._backpedalChunkHeader(stream);
        self._popInnerChunk(stream);

    def _readGeometryVertexBuffer(self, stream, mesh):
        bindIndex = self._readUShorts(stream,1)[0];
        vertexSize = self._readUShorts(stream,1)[0];
        self._pushInnerChunk(stream);
        headerID = self._readChunk(stream);
        if (headerID != OgreMeshChunkID.M_GEOMETRY_VERTEX_BUFFER_DATA):
            raise ValueError("OgreMeshSerializerImpl._readGeometryVertexBuffer: Can't find vertex buffer data area");

        pBuf = stream.read(vertexSize * );
        


    def _readGeometry(self, stream, mesh):
        vertexCount = self._readUInts(stream,1)[0];
        eof = False;
        if (not eof):
            self._pushInnerChunk(stream);
            streamID = None;
            try:
                streamID = self._readChunk(stream);
                print("streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
            except EOFError as e:
                eof = True;
            while (not eof and \
                   (streamID == OgreMeshChunkID.M_GEOMETRY_VERTEX_DECLARATION or
                    streamID == OgreMeshChunkID.M_GEOMETRY_VERTEX_BUFFER)):
                if (streamID == OgreMeshChunkID.M_GEOMETRY_VERTEX_DECLARATION):
                    print("M_GEOMETRY_VERTEX_DECLARATION");
                    self._readGeometryVertexDeclaration(stream,mesh);
                elif (streamID == OgreMeshChunkID.M_GEOMETRY_VERTEX_BUFFER):
                    print("M_GEOMETRY_VERTEX_BUFFER");
                    self._readGeometryVertexBuffer(stream,mesh);
                try:
                    streamID = self._readChunk(stream);
                    print("streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
                except EOFError as e:
                    eof = True;
            if (not eof):
                self._backpedalChunkHeader(stream);
            self._popInnerChunk(stream);


    def _readMesh(self, stream, mesh, listener):
        skeletallyAnimated = self._readBools(stream,1)[0];
        eof = False;

        while (not eof):
            self._pushInnerChunk(stream);
            streamID=None;
            try:
                streamID = self._readChunk(stream);
                print("streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
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
                    print("M_GEOMETRY");
                    self._readGeometry(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_SUBMESH):
                    print("M_SUBMESH");
                    self._readSubMesh(stream,mesh,listener);
                elif (streamID==OgreMeshChunkID.M_MESH_SKELETON_LINK):
                    print("M_MESH_SKELETON_LINK");
                    self._readSkeletonLink(stream,mesh,listener);
                elif (streamID==OgreMeshChunkID.M_MESH_BONE_ASSIGNMENT):
                    print("M_MESH_BONE_ASSIGNMENT");
                    self._readMeshBoneAssignment(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_MESH_LOD_LEVEL):
                    print("M_MESH_LOD_LEVEL");
                    self._readMeshLodLevel(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_MESH_BOUNDS):
                    print("M_MESH_BOUNDS");
                    self._readBoundsInfos(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_SUBMESH_NAME_TABLE):
                    print("M_SUBMESH_NAME_TABLE");
                    self._readSubMeshNameTable(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_EDGE_LISTS):
                    print("M_EDGE_LISTS");
                    self._readEdgeList(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_POSES):
                    print("M_POSES");
                    self._readPoses(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_ANIMATIONS):
                    print("M_ANIMATIONS");
                    self._readAnimations(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_TABLE_EXTREMES):
                    print("M_TABLE_EXTREMES");
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
            print("streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
            if (streamID == OgreMeshChunkID.M_MESH):
                print("M_MESH");
                self._readMesh(stream, mesh, listener);
            try:
                streamID = self._readChunk(stream);
            except EOFError as e:
                print("Legit end of file (no more chunks) at " + str(stream.tell()) + " exception message:" + e.message);
                eof = True;
