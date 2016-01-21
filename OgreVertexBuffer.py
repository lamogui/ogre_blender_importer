from Enum import IntEnum;


class OgreVertexElementSemantic(IntEnum):
    """
    Vertex element semantics, used to identify the meaning of vertex buffer contents
    """
    VES_UNKNOWN = 0;
    # Position, 3 reals per vertex
    VES_POSITION = 1;
    # Blending weights
    VES_BLEND_WEIGHTS = 2;
    # Blending indices
    VES_BLEND_INDICES = 3;
    # Normal, 3 reals per vertex
    VES_NORMAL = 4;
    # Diffuse colours
    VES_DIFFUSE = 5;
    # Specular colours
    VES_SPECULAR = 6;
    # Texture coordinates
    VES_TEXTURE_COORDINATES = 7;
    # Binormal (Y axis if normal is Z)
    VES_BINORMAL = 8;
    # Tangent (X axis if normal is Z)
    VES_TANGENT = 9;
    # The  number of VertexElementSemantic elements (note - the first value VES_POSITION is 1)
    VES_COUNT = 9;

class OgreVertexElementType(IntEnum):
    """
    Vertex element type, used to identify the base types of the vertex contents
    """
    VET_FLOAT1 = 0;
    VET_FLOAT2 = 1;
    VET_FLOAT3 = 2;
    VET_FLOAT4 = 3;
    # alias to more specific colour type - use the current rendersystem's colour packing
    VET_COLOUR = 4;
    VET_SHORT1 = 5;
    VET_SHORT2 = 6;
    VET_SHORT3 = 7;
    VET_SHORT4 = 8;
    VET_UBYTE4 = 9;
    # D3D style compact colour
    VET_COLOUR_ARGB = 10;
    # GL style compact colour
    VET_COLOUR_ABGR = 11;
    VET_DOUBLE1 = 12;
    VET_DOUBLE2 = 13;
    VET_DOUBLE3 = 14;
    VET_DOUBLE4 = 15;
    VET_USHORT1 = 16;
    VET_USHORT2 = 17;
    VET_USHORT3 = 18;
    VET_USHORT4 = 19;
    VET_INT1 = 20;
    VET_INT2 = 21;
    VET_INT3 = 22;
    VET_INT4 = 23;
    VET_UINT1 = 24;
    VET_UINT2 = 25;
    VET_UINT3 = 26;
    VET_UINT4 = 27;

class OgreVertexElement:
    """
    This class declares the usage of a single vertex buffer as a component
    of a complete VertexDeclaration.
    @remarks
    Several vertex buffers can be used to supply the input geometry for a
    rendering operation, and in each case a vertex buffer can be used in
    different ways for different operations; the buffer itself does not
    define the semantics (position, normal etc), the VertexElement
    class does.
    """

    def __init__(self, source, offset, theType, semantic, index):
        assert(type(source) is int and type(source) is int and type(index) is int);
        self._source = source;
        self._offset = offset;
        self._type = theType;
        self._semantic = semantic;
        self._index = index;


    def getType(self):
        return self._type;

    @property
    def semantic(self):
        return self._semantic;

    @property
    def index(self):
        return self._index;

    @property
    def offset(self):
        return self._offset;

    @property
    def source(self):
        return self._source;

    def  getTypeSize(t):
        if (t==OgreVertexElementType.VET_COLOUR or \
            t==OgreVertexElementType.VET_COLOUR_ABGR or \
            t==OgreVertexElementType.VET_COLOUR_ARGB):
            return 4;
        elif (t==OgreVertexElementType.VET_FLOAT1):
            return 4*1;
        elif (t==OgreVertexElementType.VET_FLOAT2):
            return 4*2;
        elif (t==OgreVertexElementType.VET_FLOAT3):
            return 4*3;
        elif (t==OgreVertexElementType.VET_FLOAT4):
            return 4*4;
        elif (t==OgreVertexElementType.VET_DOUBLE1):
            return 8*1;
        elif (t==OgreVertexElementType.VET_DOUBLE2):
            return 8*2;
        elif (t==OgreVertexElementType.VET_DOUBLE3):
            return 8*3;
        elif (t==OgreVertexElementType.VET_DOUBLE4):
            return 8*4;
        elif (t==OgreVertexElementType.VET_SHORT1):
            return 2*1;
        elif (t==OgreVertexElementType.VET_SHORT2):
            return 2*2;
        elif (t==OgreVertexElementType.VET_SHORT3):
            return 2*3;
        elif (t==OgreVertexElementType.VET_SHORT4):
            return 2*4;
        elif (t==OgreVertexElementType.VET_USHORT1):
            return 2*1;
        elif (t==OgreVertexElementType.VET_USHORT2):
            return 2*2;
        elif (t==OgreVertexElementType.VET_USHORT3):
            return 2*3;
        elif (t==OgreVertexElementType.VET_USHORT4):
            return 2*4;
        elif (t==OgreVertexElementType.VET_INT1):
            return 4*1;
        elif (t==OgreVertexElementType.VET_INT2):
            return 4*2;
        elif (t==OgreVertexElementType.VET_INT3):
            return 4*3;
        elif (t==OgreVertexElementType.VET_INT4):
            return 4*4;
        elif (t==OgreVertexElementType.VET_UINT1):
            return 4*1;
        elif (t==OgreVertexElementType.VET_UINT2):
            return 4*2;
        elif (t==OgreVertexElementType.VET_UINT3):
            return 4*3;
        elif (t==OgreVertexElementType.VET_UINT4):
            return 4*4;
        elif (t==OgreVertexElementType.VET_UBYTE4):
            return 4;
        return 0;

    def getTypeCount(t):
        if (t==OgreVertexElementType.VET_COLOUR or \
            t==OgreVertexElementType.VET_COLOUR_ABGR or \
            t==OgreVertexElementType.VET_COLOUR_ARGB or \
            t==OgreVertexElementType.VET_FLOAT1 or \
            t==OgreVertexElementType.VET_DOUBLE1 or \
            t==OgreVertexElementType.VET_SHORT1 or \
            t==OgreVertexElementType.VET_USHORT1 or \
            t==OgreVertexElementType.VET_INT1 or \
            t==OgreVertexElementType.VET_UINT1):
            return 1:
        elif (t==OgreVertexElementType.VET_FLOAT2 or \
              t==OgreVertexElementType.VET_DOUBLE2 or \
              t==OgreVertexElementType.VET_SHORT2 or \
              t==OgreVertexElementType.VET_USHORT2 or \
              t==OgreVertexElementType.VET_INT2 or \
              t==OgreVertexElementType.VET_UINT2):
            return 2;
        elif (t==OgreVertexElementType.VET_FLOAT3 or \
              t==OgreVertexElementType.VET_DOUBLE3 or \
              t==OgreVertexElementType.VET_SHORT3 or \
              t==OgreVertexElementType.VET_USHORT3 or \
              t==OgreVertexElementType.VET_INT3 or \
              t==OgreVertexElementType.VET_UINT3):
            return 3;
        elif (t==OgreVertexElementType.VET_FLOAT4 or \
              t==OgreVertexElementType.VET_DOUBLE4 or \
              t==OgreVertexElementType.VET_SHORT4 or \
              t==OgreVertexElementType.VET_USHORT4 or \
              t==OgreVertexElementType.VET_INT4 or \
              t==OgreVertexElementType.VET_UINT4):
            return 4;
         raise ValueError("OgreVertexElement.getTypeCount(type): Invalid type");

    def getBestCoulourVertexElementType():
        #Blender use opengl
        return OgreVertexElementType.VET_COLOUR_ABGR;

    def __eq__(self, other):
        if (self._source == other._source and \
            self._index == other._index and \
            self._offet == other._offset and \
            self._semantic == other._semantic and \
            self._type == other._type):
            return True:
        else:
            return False;


    def getSize(self):
        return getTypeSize(self._type);

class OgreVertexDeclaration:
    """
    This class declares the format of a set of vertex inputs, which
        can be issued to the rendering API through a RenderOperation.
    @remarks
    You should be aware that the ordering and structure of the
    VertexDeclaration can be very important on DirectX with older
    cards,so if you want to maintain maximum compatibility with
    all render systems and all cards you should be careful to follow these
    rules:<ol>
    <li>VertexElements should be added in the following order, and the order of the
    elements within a shared buffer should be as follows:
    position, blending weights, normals, diffuse colours, specular colours,
            texture coordinates (in order, with no gaps)</li>
    <li>You must not have unused gaps in your buffers which are not referenced
    by any VertexElement</li>
    <li>You must not cause the buffer & offset settings of 2 VertexElements to overlap</li>
    </ol>
    Whilst GL and more modern graphics cards in D3D will allow you to defy these rules,
    sticking to them will ensure that your buffers have the maximum compatibility.
    @par
    Like the other classes in this functional area, these declarations should be created and
    destroyed using the HardwareBufferManager.
    """
    def __init__(self):
        self._elementList = [];

    def getElements(self):
        return self._elementList;

    def addElement(self, source, offset, theType, semantic, index):
        if (theType == OgreVertexElementType.VET_COLOUR):
            theType = OgreVertexElement.getBestCoulourVertexElementType();
        self._elementList.append(OgreVertexElement(source,offset,theType,semantic,index));
        return self._elementList[-1];

    def insertElement(self, atPosition, source, offset, theType, semantic, index):
        if (atPosition >= len(_elementList)):
            return self.addElement(source,offset,theType,semantic,index);
        _elementList.insert(atPosition,OgreVertexElement(source,offset,theType,semantic,index));
        return _elementList[-1];

    def getElement(self, index):
        return self._elementList[index];

    def removeElement(self, index):
        del self._elementList[index];

    def removeElementWithSemantic(self, semantic, index):
        for i in range(self._elementList):
            if (self._elementList[i].semantic == semantic and self._elementList[i].index == index):
                del self._elementList[i];
                break;

    def removeAllElements(self):
        self._elementList = [];

    def findElementBySemantic(self, sem, index):
        for e in self._elementList:
            if (e.semantic == sem and e.index == index)
                return e;
        return None;

    def findElementBySource(self,source):
        return [e for e in self._elementList if e.source == source];

    def getVertexSize(self, source):
        sz = 0;
        for e in self._elementList:
            if (e.source == source):
                sz += e.getSize();
        return sz;
    
