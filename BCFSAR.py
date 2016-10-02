import sys
import os
import string
import NW4Objects
from util import *


class strg(object):
    name = ""
    size = None
    offset = None
    def __init__(self, id):
        self.id = id

class audio(object):
    name = ""
    fileID = None
    setID = None
    strgID = None
    bankID = None
    def __init__(self, setID = None):
        self.setID = setID

class soundSet(object):
    offset = None
    fileID = None
    strgID = None
    start = None
    end = None
    warc = None
    def __init__(self, id):
        self.id = id
        
class sarFile(object):
    fileName = ""
    path = ""
    tempPath = None
    offset = None
    ext = ".b"
    internal = False
    fileOffset = None
    fileInfoLength = None
    size = None
    bank = None
    def __init__(self, id):
        self.id = id

class bwav(object):
    
    def __init__(self, id):
        self.id = id

class warc(object):
    offset = None
    fileID = None
    sectionCount = None
    wavCount = None
    infoLength = None
    wavs = []
    name = ""
    folder = ""
    def __init__(self, id):
        self.id = id

class bank(object):
    offset = None
    fileID = None
    wavs = []
    seqs = []
    name = ""
    folder = ""
    def __init__(self, id):
        self.id = id

sounds = {}        
le = True
sar = open(sys.argv[1], 'rb')
sar.seek(1)
assert sar.read(3) == "SAR"
byteOrder = readu16be(sar)
print hex(byteOrder)
if byteOrder == 0xfeff:
    le = False
else:
    print "not found"
#print endian    
sar.seek(0x10)
sectionCount = readu16(sar, le)
sar.seek(2, 1)
#print sectionCount
#print sys.argv[1] + " opened"
for s in range(0, sectionCount):
    ID = readu16(sar, le)
#    print hex(ID)
    sar.seek(2, 1)
    if ID == 0x2000:
        strgOffset = readu32(sar, le)
        strgSize = readu32(sar, le)
    elif ID == 0x2001:
        infoOffset = readu32(sar, le)
        infoSize = readu32(sar, le)
    elif ID == 0x2002:
        fileOffset = readu32(sar, le)
        fileSize = readu32(sar, le)
        
# Reading STRG section
sar.seek(strgOffset)
assert sar.read(4) == "STRG"
assert readu32(sar, le) == strgSize

for s in range(0, 2):
    ID = readu16(sar, le)
#    print hex(ID)
    sar.seek(2, 1)
    if ID == 0x2400:
        strgTableOffset = readu32(sar, le) + strgOffset + 8
    elif ID == 0x2401:
        strgOtherOffset = readu32(sar, le) + strgOffset + 8

sar.seek(strgTableOffset)
strgCount = readu32(sar, le)
names = []
for i in range(strgCount):
    names.append(strg(i))
    ID = readu16(sar, le)
    sar.seek(2, 1)
    if ID ==  0x1f01:
        names[i].offset = readu32(sar, le) + strgTableOffset
        names[i].size = readu32(sar, le)
        tempPos = sar.tell()
        sar.seek(names[i].offset)
        names[i].name = sar.read(names[i].size-1)
        #print names[i].name
        sar.seek(tempPos)
    else:    # string may be null
        pass

        
# Reading INFO section
sar.seek(infoOffset)
assert sar.read(4) == "INFO"
assert readu32(sar, le) == infoSize
for i in range(8):
    ID = readu16(sar, le)
#    print hex(ID)
    sar.seek(2, 1)
    if ID == 0x2100:
        audioTableOffset = readu32(sar, le) + infoOffset + 8
    elif ID == 0x2101:
        bankTableOffset = readu32(sar, le) + infoOffset + 8
    elif ID == 0x2102:
        playerTableOffset = readu32(sar, le) + infoOffset + 8
    elif ID == 0x2103:
        warcTableOffset = readu32(sar, le) + infoOffset + 8
    elif ID == 0x2104:
        setTableOffset = readu32(sar, le) + infoOffset + 8
        #print(hex(setTableOffset))
    elif ID == 0x2105:
        groupTableOffset = readu32(sar, le) + infoOffset + 8
    elif ID == 0x2106:
        fileTableOffset = readu32(sar, le) + infoOffset + 8
    elif ID == 0x220B:
        fileTableEnd = readu32(sar, le) + infoOffset + 8
    else:
        print "Unknown table pointer"
        sar.close()
        sys.exit()

# process file table
sar.seek(fileTableOffset)
fileCount = readu32(sar, le)
files = []
fileData = {}
for i in range(fileCount):
    sar.seek(fileTableOffset + 4 + i * 8)
    files.append(sarFile(i))
    ID = readu16(sar, le)
#    print hex(ID)
    sar.seek(2, 1)
    if ID == 0x220a:
#        print "exists"
        files[i].offset = readu32(sar, le) + fileTableOffset
    else:
        print "File doesn't exist"
        sar.seek(4, 1)
    sar.seek(files[i].offset)
    ID = readu16(sar, le)
#    print hex(ID)
    sar.seek(10, 1)    
    if ID == 0x220c:
        files[i].internal = True
        ID = readu16(sar, le)
        sar.seek(2, 1)
        if ID != 0xffff:
            offset = readu32(sar, le)
            if offset != 0xffffffff:
                files[i].fileOffset = offset + fileOffset + 8
                files[i].size = readu32(sar, le)
                sar.seek(files[i].fileOffset)
                files[i].ext += string.lower(sar.read(4))
                files[i].tempPath = files[i].ext[-3:] + "/" + hex(i) + files[i].ext
                
                if not os.path.exists(files[i].tempPath):
                    outWSD = open(files[i].tempPath, 'wb')
                    sar.seek(files[i].fileOffset)
                    outWSD.write(sar.read(files[i].size))
                    outWSD.close()
                if files[i].ext.endswith("wsd"):
                    fileData[i] = NW4Objects.WSD(files[i].tempPath, 'rb')
                    fileData[i].parseHeader()
                    fileData[i].parseInfo()
                elif files[i].ext.endswith("war"):
                    fileData[i] = NW4Objects.WAR(files[i].tempPath, 'rb')
                    #fileData[i].parseHeader()
                    #fileData[i].parseInfo()
                    #print(fileData[i].wavs)
                
#                print files[i].ext                
    elif ID == 0x220d:
        files[i].path = getString(sar)
#        print files[i].path
#print(fileData)        
# process wave archive table
warcs = {}
warcFiles = {}
sar.seek(warcTableOffset)
warcCount = readu32(sar, le)
for i in range(warcCount):
    warcs[i] = warc(i)
    sar.seek(warcTableOffset + 4 + i * 8)
    ID = readu16(sar, le)
#    print hex(ID)
    sar.seek(2, 1)
    if ID == 0x2207:
        warcs[i].offset = readu32(sar, le)
        sar.seek(warcTableOffset + warcs[i].offset)
#        print hex(sar.tell())
        warcs[i].fileID = readu32(sar, le)

#looping through warcs again to see which ones have a name
for i in range(warcCount):
    fileID = warcs[i].fileID
    if i < warcCount - 1:
        warcs[i].infoLength = warcs[i+1].offset - warcs[i].offset
    else:
        warcs[i].infoLength = groupTableOffset - warcTableOffset - warcs[i].offset
    if warcs[i].infoLength > 0xc:
        sar.seek(warcTableOffset + warcs[i].offset + 0xc)
        strgID = readu32(sar, le)
        warcs[i].name = names[strgID].name
    else:
        warcs[i].name = "WARC_%s" % hex(i)
    files[fileID].fileName = warcs[i].name + files[fileID].ext
    #print("%s - %s" % (hex(i), warcs[i].name))
    #print("%s - %s" % (hex(i), files[fileID].fileName))
    # now to process wave archive
    if files[fileID].internal and files[fileID].fileOffset != None:
        """
        warcFiles[i] = NW4Objects.WAR(files[fileID].tempPath, 'rb')
        warcFiles[i].parseHeader()
        warcFiles[i].parseInfo()
        """
        sar.seek(files[fileID].fileOffset+1)
#        print hex(sar.tell())
#        print sar.read(4)
        assert sar.read(3) == "WAR"
        sar.seek(files[fileID].fileOffset)
        """
        war = open(files[fileID].fileName, "wb")
        war.write(sar.read(files[fileID].size))
        war.close()
        """
        # to be finished

# process set table
sets = []
sar.seek(setTableOffset)
setCount = readu32(sar, le)
for i in range(setCount):
    sets.append(soundSet(i))
    sar.seek(setTableOffset + 4 + i * 8)
    ID = readu16(sar, le)
    sar.seek(2, 1)
    if ID == 0x2204:
        sets[i].offset = readu32(sar, le)
        sar.seek(setTableOffset + sets[i].offset)
        
        sets[i].start = readu32(sar, le) & 0xffff # First sound ID for set
        sets[i].end = readu32(sar, le) & 0xffff # Final sound ID for set
        if sets[i].start != 0xffff:
            for j in range(sets[i].start, sets[i].end+1):
                sounds[j] = audio(setID=i)
        
        sar.seek(8,1)    
        tempID = readu16(sar, le)
        if tempID == 0x2205:
            sar.seek(0xa,1)
        else:
            sar.seek(0xa,1)
        sets[i].strgID = readu32(sar, le)
        
        #if sets[i].end != sets[i].start:
        if not (os.path.exists(names[sets[i].strgID].name)):
                os.mkdir(names[sets[i].strgID].name)
            
        sar.seek(4,1)
        sets[i].fileID = readu32(sar, le)
        print("Sound Set %s - %s - %s currently at %s for %s" % (hex(i), hex(sets[i].fileID), hex(sets[i].strgID), hex(sar.tell()), names[sets[i].strgID].name))
        if sets[i].fileID != 0xffffffff:
            
            try:
                files[sets[i].fileID].fileName = names[sets[i].strgID].name + files[sets[i].fileID].ext
            except IndexError as e:
                print(IndexError)
                
        #sar.seek(0x10,1)
        #sets[i].warc = readu32(sar, le) & 0xffff
        
# process bank table
banks = []
sar.seek(bankTableOffset)
bankCount = readu32(sar, le)
#print bankCount
for i in range(bankCount):
    banks.append(bank(i))
    sar.seek(bankTableOffset + 4 + i * 8)
    ID = readu16(sar, le)
    sar.seek(2, 1)
    if ID == 0x2206:
        banks[i].offset = readu32(sar, le)
        sar.seek(bankTableOffset + banks[i].offset)
        fileID = banks[i].fileID = readu32(sar, le)
        sar.seek(0xc,1)
        strgID = banks[i].strgID = readu32(sar, le)
        banks[i].name = names[strgID].name
        # now to process bank
        if files[fileID].internal and files[fileID].fileOffset != None:
            sar.seek(files[fileID].fileOffset+1)
#            print hex(sar.tell())
#            print sar.read(4)
            assert sar.read(3) == "BNK"
            # to be finished

            
            

# process audio table

sar.seek(audioTableOffset)
audioCount = readu32(sar, le)
#print audioCount
for i in range(audioCount):
    sar.seek(audioTableOffset + 4 + i * 8)
    ID = readu16(sar, le)
#    print hex(ID)
    sar.seek(2, 1)
    if ID == 0x2200:
        if i not in sounds:
            sounds[i] = audio()
        sounds[i].offset = readu32(sar, le) + audioTableOffset
        sar.seek(sounds[i].offset)
        fileID = sounds[i].fileID = readu32(sar, le)
        sar.seek(8,1)
        typeID = readu16(sar, le)
        sar.seek(2,1)
        nextID = readu32(sar, le)
        sar.seek(4,1)
        strgID = sounds[i].strgID = readu32(sar, le)
        sounds[i].name = names[strgID].name
        #files[fileID].fileName = sounds[i].name + files[fileID].ext
            
        if typeID == 0x2201:    # External stream
            pass
            
        if files[fileID].internal:
            if typeID == 0x2202:    # Wave sound
                WSD = None
                WAR = None
                wsd_id = None
                wsd_waves = None
                wsd_warc_id = None
                sar.seek(nextID - 0x1c, 1)
                wsd_id = readu32(sar, le)
                if files[fileID].tempPath != None:
                    if (os.path.exists(files[fileID].tempPath)):
                        #print("%s - %s - %s - %s - %s" % (hex(fileID), files[fileID].fileName, hex(sounds[i].offset), hex(files[fileID].offset), hex(files[fileID].fileOffset)))
                        """
                        WSD = NW4Objects.WSD(files[fileID].tempPath, 'rb')
                        WSD.parseHeader()
                        WSD.parseInfo()
                        """
                        #wsd_warc_id = WSD.getWarcID(wsd_id)
                        if len(fileData[fileID].waveSounds) > wsd_id:
                            wsd_warc_id = fileData[fileID].waveSounds[wsd_id][0]
                            #wsd_warc_wav = WSD.getWarcWavID(wsd_id)
                            wsd_warc_wav = fileData[fileID].waveSounds[wsd_id][1]
                            #print("Wave sound %s - Wave archive %s - Binary wav %s" % (hex(wsd_id), hex(wsd_warc_id), hex(wsd_warc_wav)))
                            """
                            WAR = NW4Objects.WAR(files[warcs[wsd_warc_id].fileID].tempPath, 'rb')
                            WAR.parseHeader()
                            WAR.parseInfo()
                            #if string.find(sounds[i].name, "CHROM") != -1:
                            #print(len(wsd_waves))
                           
                            WAR.seek(WAR.wavs[wsd_warc_wav][0])
                            """
                            fileData[warcs[wsd_warc_id].fileID].parseHeader()
                            fileData[warcs[wsd_warc_id].fileID].parseInfo()
                            print("%s - %s (%s) - %s - %s - %s at offset %s, size %s" % (files[fileID].tempPath, sounds[i].name, hex(wsd_warc_wav), hex(wsd_warc_id), files[warcs[wsd_warc_id].fileID].tempPath, warcs[wsd_warc_id].name, hex(fileData[warcs[wsd_warc_id].fileID].wavs[wsd_warc_wav][0]), hex(fileData[warcs[wsd_warc_id].fileID].wavs[wsd_warc_wav][1])))
                            if sounds[i].setID != None:
                                outfile = open(names[sets[sounds[i].setID].strgID].name + "/" + sounds[i].name + files[fileID].ext[:3] + "wav", 'wb')
                            else:
                                outfile = open("wsd/wavs/" + sounds[i].name + files[fileID].ext[:3] + "wav", 'wb')
                            #WAR.seek(-4, 1)
                            fileData[warcs[wsd_warc_id].fileID].seek(fileData[warcs[wsd_warc_id].fileID].wavs[wsd_warc_wav][0])
                            outfile.write(fileData[warcs[wsd_warc_id].fileID].read(fileData[warcs[wsd_warc_id].fileID].wavs[wsd_warc_wav][1]))
                            outfile.close()
                        else:
                            pass
                            #WSD.close()
                   
            elif typeID == 0x2203:    # Sequence
                sar.seek(0x40,1)
                if fileID == 207:
                    print hex(sar.tell())
                bankID = sounds[i].bankID = readByte(sar)
    #            print hex(bankID)
    #            banks[sounds[i].bankID].seqs.append(1)
                sar.seek(files[fileID].fileOffset+1)
                assert sar.read(3) == "SEQ"


#for i in range(bankCount):
#    print banks[i].name
#    print "\t" + str(len(banks[i].seqs))
#    for j in range(len(banks[i].seqs)):
#        print "\t" + files[banks[i].seqs[j]].fileName

for key in sounds:
    print("%s - %s" % (hex(key), sounds[key].name))

for f in files:
    if f.internal:
        print("%s - %s" % (hex(f.id), f.fileName))
    else:
        print("%s - %s" % (hex(f.id), f.path))
     
        
sar.close()
"""
if os.path.exists(f.tempPath) and not os.path.exists(os.path.join(os.path.split(f.tempPath)[0], f.fileName+f.ext)):
    os.rename(os.path.normpath(f.tempPath), os.path.join(os.path.split(f.tempPath)[0], f.fileName+f.ext))
"""