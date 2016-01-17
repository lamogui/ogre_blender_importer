
from enum import IntEnum;
from io import IOBase;
from io import SEEK_CUR;
from struct import unpack;

class OgreSerializer:
    """
    Generic class for serialising data to / from binary stream-based files.
    This class provides a number of useful methods for exporting / importing data
    from stream-oriented binary files (e.g. .mesh and .skeleton)
    From: OgreMain/include/OgreSerializer.h and OgreMain/src/OgreSerializer.cpp
    url: https://bitbucket.org/sinbad/ogre/src/0d580c7216abe27fafe41cb43e31d8ed86ded591/OgreMain/include/OgreSerializer.h
    """

    class Endian(IntEnum):
        ENDIAN_NATIVE = 1;
        ENDIAN_BIG = 2;
        ENDIAN_LITTLE = 3;

    def __init__(self):
        self._version("[Serializer_v1.00]");
        self._flipEndian=False;

    def _determineEndianness(self,stream):
        assert(issubclass(type(stream),IOBase));

        if (stream.readable()):
            raise ValueError("OgreSerializer._determineEndianness(self,stream): "
                             "Stream not readable !");
        else if (stream.tell() != 0):
            raise IndexError("OgreSerializer._determineEndianness(self,stream):"
                             " Can only determine the endianness of the input "
                             "stream if it is at the start");
        actually_read = stream.read(2);
        stream.seek(0 - len(actually_read), SEEK_CUR);
        if (len(actually_read) != 2):
            raise IndexError("OgreSerializer._determineEndianness(self,stream):"
                             " Couldn't read 16 bit header value from input stream");
        dest = unpack("",actually_read)
