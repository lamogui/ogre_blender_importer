from OgreMeshSerializerImpl import *
from OgreSerializer import OgreSerializer
from OgreMeshVersion import OgreMeshVersion
from io import SEEK_SET;

class OgreMeshSerializer(OgreSerializer):
    """
    Class for serialising mesh data to/from an OGRE .mesh file.
    @remarks
        This class allows exporters to write OGRE .mesh files easily, and allows the
        OGRE engine to import .mesh files into instantiated OGRE Meshes.
        Note that a .mesh file can include not only the Mesh, but also definitions of
        any Materials it uses (although this is optional, the .mesh can rely on the
        Material being loaded from another source, especially useful if you want to
        take advantage of OGRE's advanced Material properties which may not be available
        in your modeller).
    @par
        To export a Mesh:<OL>
        <LI>Use the MaterialManager methods to create any dependent Material objects, if you want
            to export them with the Mesh.</LI>
        <LI>Create a Mesh object and populate it using it's methods.</LI>
        <LI>Call the exportMesh method</LI>
        </OL>
    @par
        It's important to realise that this exporter uses OGRE terminology. In this context,
        'Mesh' means a top-level mesh structure which can actually contain many SubMeshes, each
        of which has only one Material. Modelling packages may refer to these differently, for
        example in Milkshape, it says 'Model' instead of 'Mesh' and 'Mesh' instead of 'SubMesh',
        but the theory is the same.
    """

    HEADER_CHUNK_ID = 0x1000;

    class _MeshVersionData:
        def __init__(self, _ver, _string, _impl):
            self.version=_ver;
            self.versionString=_string;
            self.impl=_impl;

    def __init__(self):
        OgreSerializer.__init__(self);
        self.listener=None;
        self._versionData = [];
        self._versionData.append(_MeshVersionData(OgreMeshVersion.MESH_VERSION_1_10, "[MeshSerializer_v1.100]",OgreMeshSerializerImpl()));

    def importMesh(self, stream, mesh):
        assert(issubclass(type(stream),IOBase));
        self._determineEndianness(stream);
        headerID = self._readUShorts(stream,1)[0];
        if (headerID != HEADER_CHUNK_ID):
            raise ValueError("File header not found");
        ver = self._readString(stream);
        stream.seek(0,SEEK_SET);
        impl = None;
        for i in self._versionData:
            if (i.versionString == ver):
                impl = i.impl;
                break;
        if (impl is None):
            raise ValueError("Cannot find serializer implementation for "
                             "mesh version " + ver);
        impl.importMesh(stream,mesh,self.listener);
        if (ver != self._versionData[0].versionString):
            print("WARNING: "
                  " older format (" + ver + "); you should upgrade it as soon as possible" +
                  " using the OgreMeshUpgrade tool.");
        if (self.listener is not None):
            listener.processMeshCompleted(mesh);
