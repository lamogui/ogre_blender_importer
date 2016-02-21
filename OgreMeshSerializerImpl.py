import bpy
import mathutils
import io;

try:
    from OgreSerializer import OgreSerializer
    from OgreVertexIndexData import *
    from OgreVertexBuffer import *
    from OgreMeshFileFormat import *
    from OgreHardwareBuffer import *

except ImportError as e:
    print("Import error: " + str(e) + " manual compilation" );
    srcfile="OgreSerializer.py"; exec(compile(open(srcfile).read(), srcfile, 'exec'))
    srcfile="OgreVertexIndexData.py"; exec(compile(open(srcfile).read(), srcfile, 'exec'))
    srcfile="OgreVertexBuffer.py"; exec(compile(open(srcfile).read(), srcfile, 'exec'))
    srcfile="OgreMeshFileFormat.py"; exec(compile(open(srcfile).read(), srcfile, 'exec'))
    srcfile="OgreHardwareBuffer.py"; exec(compile(open(srcfile).read(), srcfile, 'exec'))


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


    def _readGeometryVertexElement(self,stream,mesh,dest, pstr_indent_lvl):

        str_indent_lvl = pstr_indent_lvl + "  ";

        source = self._readUShorts(stream,1)[0]; #Buffer ogre correspondant ?
        vType = self._readUShorts(stream,1)[0];  #Type de valeur
        vSemantic = self._readUShorts(stream, 1)[0]; #Utilité du vertex
        offset = self._readUShorts(stream, 1)[0]; #always 0 ?
        index = self._readUShorts(stream, 1)[0];  #always 0 ?
        dest.vertexDeclaration.addElement(source,offset,vType,vSemantic, index)
        print(str_indent_lvl + "source: " + str(source));
        print(str_indent_lvl + "type: " + OgreVertexElementType.toStr(vType));
        print(str_indent_lvl + "semantic: " + OgreVertexElementSemantic.toStr(vSemantic));
        print(str_indent_lvl + "offset: " + str(offset))
        print(str_indent_lvl + "index: " + str(index));


    def _readGeometryVertexDeclaration(self,stream,mesh,dest, pstr_indent_lvl):
        self._pushInnerChunk(stream);
        streamID = None;
        eof = False;

        str_indent_lvl = pstr_indent_lvl + "  ";

        try:
            streamID = self._readChunk(stream);
            #print(str_indent_lvl + "streamID " + "{0:#04x}".format(streamID) + " (offset: {0:#0x})".format(stream.tell()));
        except EOFError as e:
            eof = True;
        while (not eof and streamID == OgreMeshChunkID.M_GEOMETRY_VERTEX_ELEMENT):
            if (streamID == OgreMeshChunkID.M_GEOMETRY_VERTEX_ELEMENT):
                print(str_indent_lvl + "M_GEOMETRY_VERTEX_ELEMENT");
                self._readGeometryVertexElement(stream,mesh,dest,str_indent_lvl);
            try:
                streamID = self._readChunk(stream);
                #print(str_indent_lvl + "streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
            except EOFError as e:
                eof = True;
        if (not eof):
            self._backpedalChunkHeader(stream);
        self._popInnerChunk(stream);

    def _readGeometryVertexBuffer(self, stream, mesh, dest, pstr_indent_lvl):
        bindIndex = self._readUShorts(stream,1)[0];
        vertexSize = self._readUShorts(stream,1)[0];

        str_indent_lvl = pstr_indent_lvl + "  ";

        print(str_indent_lvl + "bind index: " + str(bindIndex));
        print(str_indent_lvl + "vertex size: " + str(vertexSize));

        self._pushInnerChunk(stream);
        headerID = self._readChunk(stream);
        if (headerID != OgreMeshChunkID.M_GEOMETRY_VERTEX_BUFFER_DATA):
            raise ValueError("OgreMeshSerializerImpl._readGeometryVertexBuffer: Can't find vertex buffer data area");

        #Check that vertex size agrees
        if (dest.vertexDeclaration.getVertexSize(bindIndex) != vertexSize):
            raise ValueError("OgreMeshSerializerImpl._readGeometryVertexBuffer: Buffer vertex size does not agree with vertex declarationBuffer vertex size does not agree with vertex declaration");

        if (OgreSerializer.Endian.ENDIAN_NATIVE != self._endianness):
            raise NotImplementedError;
        else:
            hb = OgreVertexBuffer(vertexSize,dest.vertexCount);
            hb.data = stream.read(dest.vertexCount*vertexSize);
            print(str_indent_lvl + "buffered " + str(len(hb.data)) + " elements");
            dest.vertexBufferBinding.setBinding(bindIndex,hb);
        self._popInnerChunk(stream);




    def _readGeometry(self, stream, mesh, dest, pstr_indent_lvl):
        dest.vertexStart = 0;
        dest.vertexCount = self._readUInts(stream,1)[0];

        str_indent_lvl = pstr_indent_lvl + "  ";

        print(str_indent_lvl + "Vertex count: " + str(dest.vertexCount));
        eof = False;

        if (not eof):
            self._pushInnerChunk(stream);
            streamID = None;
            try:
                streamID = self._readChunk(stream);
                print(str_indent_lvl + "streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
            except EOFError as e:
                eof = True;
            while (not eof and \
                   (streamID == OgreMeshChunkID.M_GEOMETRY_VERTEX_DECLARATION or
                    streamID == OgreMeshChunkID.M_GEOMETRY_VERTEX_BUFFER)):
                if (streamID == OgreMeshChunkID.M_GEOMETRY_VERTEX_DECLARATION):
                    print(str_indent_lvl + "M_GEOMETRY_VERTEX_DECLARATION");
                    self._readGeometryVertexDeclaration(stream,mesh,dest,str_indent_lvl);
                elif (streamID == OgreMeshChunkID.M_GEOMETRY_VERTEX_BUFFER):
                    print(str_indent_lvl + "M_GEOMETRY_VERTEX_BUFFER");
                    self._readGeometryVertexBuffer(stream,mesh,dest,str_indent_lvl);
                try:
                    streamID = self._readChunk(stream);
                    print(str_indent_lvl + "streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
                except EOFError as e:
                    eof = True;
            if (not eof):
                self._backpedalChunkHeader(stream);
            self._popInnerChunk(stream);

    def _readSubMeshOperation(self, stream, mesh, submesh, pstr_indent_lvl):
        str_indent_lvl = pstr_indent_lvl + "  ";
        opType = self._readShorts(stream,1)[0];
        print(str_indent_lvl + "Operation type: " + str(opType));
        if (opType != 4):
            raise NotImplementedError("TODO implement different modes other than OP_TRIANGLE_LIST");


    def _readSubMesh(self,stream, mesh, listener):
        streamID = None;
        eof = False;

        str_indent_lvl = "    ";

        submesh = mesh.createSubMesh();
        submesh.materialName = OgreSerializer.readString(stream);
        submesh.useSharedVertices = self._readBools(stream,1)[0];
        submesh.indexData.indexStart = 0; #always 0 because we have a separate buffer so this variable is useless
        submesh.indexData.indexCount = self._readUInts(stream,1)[0];

        print(str_indent_lvl + "Material name: " + submesh.materialName);
        print(str_indent_lvl + "Use shared vertices: " + str(submesh.useSharedVertices));
        #print(str_indent_lvl + "Index start: " + str(submesh.indexData.indexStart));
        print(str_indent_lvl + "Index count: " + str(submesh.indexData.indexCount));

        idx32bit = self._readBools(stream,1)[0];

        print(str_indent_lvl + "Index 32 bits: " + str(idx32bit));

        if (submesh.indexData.indexCount > 0):
            if (idx32bit):
                submesh.indexData.data = self._readUInts(stream,submesh.indexData.indexCount);
            else:
                submesh.indexData.data = self._readUShorts(stream,submesh.indexData.indexCount);

        self._pushInnerChunk(stream);
        if (not submesh.useSharedVertices):
            try:
                streamID = self._readChunk(stream);
                print(str_indent_lvl + "streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
            except EOFError as e:
                eof = True;
            if (streamID != OgreMeshChunkID.M_GEOMETRY):
                raise ValueError("OgreMeshSerializerImpl._readSubMesh: Missing geometry data in mesh file");
            submesh.vertexData = OgreVertexData();
            print(str_indent_lvl + "M_GEOMETRY");
            self._readGeometry(stream,mesh,submesh.vertexData,str_indent_lvl);
            raise NotImplementedError("TODO Implement support for submesh not using sharedVertexData"); #Don't support this at the moment I hop it's not commonly used


        try:
            streamID = self._readChunk(stream);
            #print(str_indent_lvl + "streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
        except EOFError as e:
            eof = True;
        while (not eof and \
               (streamID == OgreMeshChunkID.M_SUBMESH_OPERATION) or
               (streamID == OgreMeshChunkID.M_SUBMESH_BONE_ASSIGNMENT) or
               (streamID == OgreMeshChunkID.M_SUBMESH_TEXTURE_ALIAS)):
            if (streamID == OgreMeshChunkID.M_SUBMESH_OPERATION):
                print(str_indent_lvl + "M_SUBMESH_OPERATION");
                self._readSubMeshOperation(stream,mesh,submesh,str_indent_lvl);
            elif (streamID == OgreMeshChunkID.M_SUBMESH_BONE_ASSIGNMENT):
                print(str_indent_lvl + "M_SUBMESH_BONE_ASSIGNMENT");
                raise NotImplementedError("TODO implement M_SUBMESH_BONE_ASSIGNMENT");
            elif (streamID == OgreMeshChunkID.M_SUBMESH_TEXTURE_ALIAS):
                print(str_indent_lvl + "M_SUBMESH_TEXTURE_ALIAS");
                raise NotImplementedError("TODO implement M_SUBMESH_TEXTURE_ALIAS");
            try:
                streamID = self._readChunk(stream);
                #print(str_indent_lvl + "streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
            except EOFError as e:
                eof = True;

        if (not eof):
            self._backpedalChunkHeader(stream);

        self._popInnerChunk(stream);



    def _readSkeletonLink(self,stream,mesh,listener):
        str_indent_lvl = "    ";
        mesh.skeletonName = OgreSerializer.readString(stream);
        print(str_indent_lvl + "Skeleton Name: " + mesh.skeletonName);
        if (listener is not None):
            listener.processSkeletonName(mesh,name);

    def _readMeshBoneAssignment(self,stream, mesh):
        str_indent_lvl = "    ";

        vertexIndex = self._readUInts(stream,1)[0];
        boneIndex = self._readShorts(stream,1)[0];
        weight = self._readFloats(stream,1)[0];

        #So much lines in debug
        #print(str_indent_lvl + "Vertex index: " + str(vertexIndex));
        #print(str_indent_lvl + "Bone index: " + str(boneIndex));
        #print(str_indent_lvl + "Weight: " + str(weight));

    def _readBoundsInfos(self, stream, mesh):
        str_indent_lvl = "    ";

        minBound = self._readVector3(stream);
        maxBound = self._readVector3(stream);
        radius = self._readFloats(stream,1)[0];

        print(str_indent_lvl + "Min: " + str(minBound));
        print(str_indent_lvl + "Max: " + str(maxBound));
        print(str_indent_lvl + "Radius: " + str(radius));

    def _readSubMeshNameTable(self,stream, mesh):
        str_indent_lvl = "    ";

        streamID = None;
        subMeshIndex = None;
        eof = False;
        subMeshNames = {};

        self._pushInnerChunk(stream);

        try:
            streamID = self._readChunk(stream);
            #print(str_indent_lvl + "streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
        except EOFError as e:
            eof = True;
        while (not eof and (streamID == OgreMeshChunkID.M_SUBMESH_NAME_TABLE_ELEMENT)):
            subMeshIndex = self._readUShorts(stream,1)[0];
            subMeshNames[subMeshIndex] = OgreSerializer.readString(stream);
            print(str_indent_lvl + str(subMeshIndex) + ": " + subMeshNames[subMeshIndex]);
            try:
                streamID = self._readChunk(stream);
                #print(str_indent_lvl + "streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
            except EOFError as e:
                eof = True;

        if (not eof):
            self._backpedalChunkHeader(stream);

        self._popInnerChunk(stream);

    def _readEdgetListLodInfo(self,stream,edgeData):
        str_indent_lvl = "      ";

        isClosed = self._readBools(stream,1)[0];
        numTriangles = self._readUInts(stream,1)[0];
        numEdgeGroups = self._readUInts(stream,1)[0];

        print(str_indent_lvl + "Closed: " + str(isClosed));
        print(str_indent_lvl + "Triangles: " + str(numTriangles));
        print(str_indent_lvl + "Edge groups: " + str(numEdgeGroups));

        #stream.seek(numTriangles * (8 * 4 + 4 * 4), io.SEEK_SET);
        self._readUInts(stream, numTriangles * 8);
        self._readFloats(stream, numTriangles * 4);

        self._pushInnerChunk(stream);
        for eg in range(numEdgeGroups):
            streamID = self._readChunk(stream);
            if (streamID != OgreMeshChunkID.M_EDGE_GROUP):
                raise ValueError("OgreMeshSerializerImpl._readEdgetListLodInfo: Missing M_EDGE_GROUP stream");

            self._readUInts(stream,3);
            numEdges = self._readUInts(stream,1)[0];

            #stream.seek(numEdges * (6 * 4 + 1));
            self._readUInts(stream,numEdges*6);
            self._readBools(stream, numEdges);

        self._popInnerChunk(stream);

    def _readEdgeList(self,stream,mesh):
        str_indent_lvl = "    ";
        estr_indent_lvl = str_indent_lvl + "  ";

        eof = False;
        streamID = None;
        self._pushInnerChunk(stream);
        try:
            streamID = self._readChunk(stream);
            print(str_indent_lvl + "streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()) +  " (size: " + str(self._currentstreamLen) + ")");
        except EOFError as e:
            eof = True;
        while (not eof and streamID==OgreMeshChunkID.M_EDGE_LIST_LOD):
            print (str_indent_lvl + "M_EDGE_LIST_LOD");
            lodIndex = self._readUShorts(stream, 1)[0];
            isManual = self._readBools(stream,1)[0];

            print(estr_indent_lvl + "LOD Index: " + str(lodIndex));
            print(estr_indent_lvl + "Manual: " + str(isManual));

            if (not isManual):
                self._readEdgetListLodInfo(stream,None);

            streamID = self._readChunk(stream);

        if (not eof):
            self._backpedalChunkHeader(stream);
        self._popInnerChunk(stream);




    def _readMesh(self, stream, mesh, listener):

        skeletallyAnimated = self._readBools(stream,1)[0];
        print("Skeletally animated: " + str(skeletallyAnimated));

        eof = False;

        str_indent_lvl = "  ";

        while (not eof):
            self._pushInnerChunk(stream);
            streamID=None;
            try:
                streamID = self._readChunk(stream);
                #print(str_indent_lvl + "streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
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
                   streamID == OgreMeshChunkID.M_TABLE_EXTREMES)):

                if (streamID==OgreMeshChunkID.M_GEOMETRY):
                    print(str_indent_lvl + "M_GEOMETRY");
                    mesh.sharedVertexData = OgreVertexData();
                    self._readGeometry(stream,mesh, mesh.sharedVertexData, str_indent_lvl);
                elif (streamID==OgreMeshChunkID.M_SUBMESH):
                    print(str_indent_lvl + "M_SUBMESH");
                    self._readSubMesh(stream,mesh,listener);
                elif (streamID==OgreMeshChunkID.M_MESH_SKELETON_LINK):
                    print(str_indent_lvl + "M_MESH_SKELETON_LINK");
                    self._readSkeletonLink(stream,mesh,listener);
                elif (streamID==OgreMeshChunkID.M_MESH_BONE_ASSIGNMENT):
                    #print(str_indent_lvl + "M_MESH_BONE_ASSIGNMENT");
                    self._readMeshBoneAssignment(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_MESH_LOD_LEVEL):
                    print(str_indent_lvl + "M_MESH_LOD_LEVEL");
                    self._readMeshLodLevel(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_MESH_BOUNDS):
                    print(str_indent_lvl + "M_MESH_BOUNDS");
                    self._readBoundsInfos(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_SUBMESH_NAME_TABLE):
                    print(str_indent_lvl + "M_SUBMESH_NAME_TABLE");
                    self._readSubMeshNameTable(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_EDGE_LISTS):
                    print(str_indent_lvl + "M_EDGE_LISTS");
                    self._readEdgeList(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_POSES):
                    print(str_indent_lvl + "M_POSES");
                    raise NotImplementedError("TODO Implement: M_POSES");
                    self._readPoses(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_ANIMATIONS):
                    print(str_indent_lvl + "M_ANIMATIONS");
                    raise NotImplementedError("TODO Implement: M_ANIMATIONS");
                    self._readAnimations(stream,mesh);
                elif (streamID==OgreMeshChunkID.M_TABLE_EXTREMES):
                    print(str_indent_lvl + "M_TABLE_EXTREMES");
                    raise NotImplementedError("TODO Implement: M_TABLE_EXTREMES");
                    self._readExtremes(stream,mesh);

                try:
                    streamID = self._readChunk(stream);
                    #print(str_indent_lvl + "streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
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

        str_indent_lvl = "";

        eof = False;
        while (not eof):
            #print(str_indent_lvl + "streamID " + "{0:#0{1}x}".format(streamID,4) + " (offset: {0:#0x})".format(stream.tell()));
            if (streamID == OgreMeshChunkID.M_MESH):
                print("M_MESH");
                self._readMesh(stream, mesh, listener);
            try:
                streamID = self._readChunk(stream);
            except EOFError as e:
                print("Legit end of file (no more chunks) at " + str(stream.tell()) + " exception message:" + e.message);
                eof = True;
