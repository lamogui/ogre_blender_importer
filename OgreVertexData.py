from OgreVertexBuffer import *

class OgreVertexData:
    def __init__(self):
        self.vertexBufferBinding = OgreVertexBufferBinding();
        self.vertexDeclaration = OgreVertexDeclaration();
        self.vertexCount = 0;
        self.vertexStart = 0;
