import struct

def read8(file):
    return struct.unpack("b", file.read(1))[0]

def readByte(file):
    return struct.unpack("B", file.read(1))[0]

def read16(file, le=True):
    if le:
        return struct.unpack("<h", file.read(2))[0]
    else:
        return struct.unpack(">h", file.read(2))[0]
        
def readu16(file, le=True):
    if le:
        return struct.unpack("<H", file.read(2))[0]
    else:
        return struct.unpack(">H", file.read(2))[0]

def read32(file, le=True):
    if le:
        return struct.unpack("<i", file.read(4))[0]
    else:
        return struct.unpack(">i", file.read(4))[0]    
    
def readu32(file, le=True):
    if le:
        return struct.unpack("<I", file.read(4))[0]
    else:
        return struct.unpack(">I", file.read(4))[0]    
    
def readfloat(file, le=True):
    if le:
        return struct.unpack("<f", file.read(4))[0]
    else:
        return struct.unpack(">f", file.read(4))[0]
   
def getString(file):
    result = ""
    tmpChar = file.read(1)
    while ord(tmpChar) != 0:
        result += tmpChar
        tmpChar =file.read(1)
    return result
