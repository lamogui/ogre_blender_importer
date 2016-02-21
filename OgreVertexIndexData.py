
try:
    from OgreVertexBuffer import *
except ImportError as e:
    print("Import error: " + str(e) + " manual compilation" );
    srcfile="OgreVertexBuffer.py"; exec(compile(open(srcfile).read(), srcfile, 'exec'))


class OgreVertexData:
    def __init__(self):
        self.vertexBufferBinding = OgreVertexBufferBinding();
        self.vertexDeclaration = OgreVertexDeclaration();
        self.vertexCount = 0;
        self.vertexStart = 0;

class OgreIndexData:
    def __init__(self):
        self.indexStart = 0;
        self.indexCount = 0;
        self.data = None;
