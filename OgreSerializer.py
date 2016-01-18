from enum import Enum;
from io import IOBase;
from io import SEEK_CUR;
from struct import unpack;
import sys;

class OgreSerializer:
    """
    Generic class for serialising data to / from binary stream-based files.
    This class provides a number of useful methods for exporting / importing data
    from stream-oriented binary files (e.g. .mesh and .skeleton)
    From: OgreMain/include/OgreSerializer.h and OgreMain/src/OgreSerializer.cpp
    url: https://bitbucket.org/sinbad/ogre/src/0d580c7216abe27fafe41cb43e31d8ed86ded591/OgreMain/include/OgreSerializer.h
    """


    LITTLE_ENDIAN_HEADER_STREAM_ID = 0x1000;
    BIG_ENDIAN_HEADER_STREAM_ID = 0x0010;

    class Endian(Enum):
        ENDIAN_NATIVE = sys.byteorder;
        ENDIAN_BIG = 'big';
        ENDIAN_LITTLE = 'little';
    def __init__(self):
        self._version("[Serializer_v1.00]");
        self._endianness=ENDIAN_NATIVE;
    def _determineEndianness(self,param):
        if issubclass(type(param, IOBase)):
            stream = param;
            if (stream.readable()):
                raise ValueError("OgreSerializer._determineEndianness(self,stream): "
                                 "Stream not readable !");
            else if (stream.tell() != 0):
                raise ValueError("OgreSerializer._determineEndianness(self,stream):"
                                 " Can only determine the endianness of the input "
                                 "stream if it is at the start");
            actually_read = stream.read(2);
            stream.seek(0 - len(actually_read), SEEK_CUR);
            if len(actually_read) != 2:
                raise ValueError("OgreSerializer._determineEndianness(self,stream):"
                                 " Couldn't read 16 bit header value from input stream");
            dest = unpack("=H",actually_read)[0];
            if dest == LITTLE_ENDIAN_HEADER_STREAM_ID:
                self._endianness = ENDIAN_LITTLE;
            else if dest == BIG_ENDIAN_HEADER_STREAM_ID:
                self._endianness = ENDIAN_BIG;
            else:
                raise ValueError("OgreSerializer._determineEndianness(self,stream): "
                                 "Header chunk didn't match either endian: Corrupted stream?");
        else if param == ENDIAN_BIG or param == ENDIAN_LITTLE:
            self._endianness = param;
        else:
            raise raise ValueError("OgreSerializer._determineEndianness(self,param): "
                                    "Invalid parameter should be an IOBase class or 'little' or 'big'");
    def _readBools(self, stream, count):
        assert(issubclass(type(stream),IOBase));
        assert(type(count) is int and count > 0);
        readed = stream.read(count);
        if self._endianness==ENDIAN_LITTLE:
            return unpack("<" + ("?"*count), readed);
        else:
            return unpack(">" + ("?"*count), readed);
    def _readFloats(self, stream, count):
        assert(issubclass(type(stream),IOBase));
        assert(type(count) is int and count > 0);
        readed = stream.read(count*4);
        if self._endianness==ENDIAN_LITTLE:
            return unpack("<" + ("f"*count), readed);
        else:
            return unpack(">" + ("f"*count), readed);
    def _readDoubles(self, stream, count):
        assert(issubclass(type(stream),IOBase));
        assert(type(count) is int and count > 0);
        readed = stream.read(count*8);
        if self._endianness==ENDIAN_LITTLE:
            return unpack("<" + ("d"*count), readed);
        else:
            return unpack(">" + ("d"*count), readed);
    def _readShorts(self, stream, count):
        assert(issubclass(type(stream),IOBase));
        assert(type(count) is int and count > 0);
        readed = stream.read(count*2);
        if self._endianness==ENDIAN_LITTLE:
            return unpack("<" + ("h"*count), readed);
        else:
            return unpack(">" + ("h"*count), readed);
    def _readUShorts(self, stream, count):
        assert(issubclass(type(stream),IOBase));
        assert(type(count) is int and count > 0);
        readed = stream.read(count*2);
        if self._endianness==ENDIAN_LITTLE:
            return unpack("<" + ("H"*count), readed);
        else:
            return unpack(">" + ("H"*count), readed);
    def _readInts(self, stream, count):
        assert(issubclass(type(stream),IOBase));
        assert(type(count) is int and count > 0);
        readed = stream.read(count*4);
        if self._endianness==ENDIAN_LITTLE:
            return unpack("<" + ("i"*count), readed);
        else:
            return unpack(">" + ("i"*count), readed);
    def _readUInts(self, stream, count):
        assert(issubclass(type(stream),IOBase));
        assert(type(count) is int and count > 0);
        readed = stream.read(count*4);
        if self._endianness==ENDIAN_LITTLE:
            return unpack("<" + ("I"*count), readed);
        else:
            return unpack(">" + ("I"*count), readed);
    def _readString(self, stream, size=-1):
        assert(issubclass(type(stream),IOBase));
        stream.readline(size);
