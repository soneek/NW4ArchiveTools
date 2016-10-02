import struct
import sys

class SoneekFile(file):
    def readu32(self, le=True):
        if le:
            return struct.unpack("<I", self.read(4))[0]
        else:
            return struct.unpack(">I", self.read(4))[0]
    
    def readu16(self, le=True):
        if le:
            return struct.unpack("<H", self.read(2))[0]
        else:
            return struct.unpack(">H", self.read(2))[0]
            
class WAR(SoneekFile):
    # Wave archives (B(R/C/F)WAR)
    wavs = {}
            
    def parseHeader(self):
        self.seek(0)
        self.war_type = self.read(4)
        if self.readu16(True) == 0xfeff:
            self.le = True
        else:
            self.le = False
        headerSize = self.readu16(self.le)
        self.seek(0x10)
        sectionCount = self.readu16(self.le)
        self.seek(2,1)
        for i in range(sectionCount):
            sectionType = self.readu16(self.le)
            self.seek(2,1)
            sectionOffset = self.readu32(self.le)
            sectionSize = self.readu32(self.le)
            if sectionType == 0x6800: # INFO
                self.infoOffset = sectionOffset
                self.infoSize = sectionSize
            elif sectionType == 0x6801: # FILE
                self.fileOffset = sectionOffset
                self.fileSize = sectionSize
            else:
                print("Unknown section ID %s" % (hex(sectionType)))
                
    def parseInfo(self):
        self.seek(self.infoOffset)
        if self.read(4) != "INFO": 
            self.close()
            sys.exit("Not the INFO section!")
        if self.readu32(self.le) != self.infoSize:
            self.close()
            sys.exit("Mismatch")
        self.wavCount = self.readu32(self.le)
        for i in range(self.wavCount):
            self.seek(self.infoOffset + 0xc + i * 0xc)
            if self.readu16(self.le) != 0x1f00:
                self.close()
                sys.exit("Not a valid header")
            self.seek(2,1)
            wavOffset = self.readu32(self.le)
            wavSize = self.readu32(self.le)
            self.wavs[i] = [self.fileOffset + 8 + wavOffset, wavSize]
            #print("%s - %s - %s" % (hex(i), hex(self.wavs[i][0]), hex(self.wavs[i][1])))
            
class WSD(SoneekFile):

    def parseHeader(self):
        self.seek(0)
        self.war_type = self.read(4)
        if self.readu16(True) == 0xfeff:
            self.le = True
        else:
            self.le = False
        headerSize = self.readu16(self.le)
        self.seek(0x10)
        sectionCount = self.readu16(self.le)
        self.seek(2,1)
        for i in range(sectionCount):
            sectionType = self.readu16(self.le)
            self.seek(2,1)
            sectionOffset = self.readu32(self.le)
            sectionSize = self.readu32(self.le)
            if sectionType == 0x6800: # INFO
                self.infoOffset = sectionOffset
                self.infoSize = sectionSize
            elif sectionType == 0x6801: # FILE
                self.fileOffset = sectionOffset
                self.fileSize = sectionSize
            else:
                print("Unknown section ID %s" % (hex(sectionType)))
    
    def parseInfo(self):
        self.waveSounds = {}
        self.seek(self.infoOffset)
        if self.read(4) != "INFO": 
            self.close()
            sys.exit("Not the INFO section!")
        if self.readu32(self.le) != self.infoSize:
            self.close()
            sys.exit("Mismatch")
        self.seek(0x10, 1)
            
        wavCount = self.readu32(self.le)
        #print(wavCount)
        for i in range(wavCount):
            warc = self.readu32(self.le) - 0x5000000
            wavID = self.readu32(self.le)
            self.waveSounds[i] = [warc, wavID]
        print(len(self.waveSounds) == wavCount)
    def getWarcID(self, wav):
        return self.waveSounds[wav][0]
    def getWarcWavID(self, wav):
        return self.waveSounds[wav][1]
        