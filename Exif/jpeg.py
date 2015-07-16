import binascii
from struct import unpack_from

from .tags import *

"""
Exif Data Structure [Bytes]:
    Header :
        1-2     : Section declaration (hex)
        3-4     : Section length (int)
        5-8     : Section header name (ascii)
        9-10    : Zero bytes
        11-12   : Bytes order (Big/Little Endian, ...)
        #13-14   : 42
        #15-18   : IFD offset
    Image File Directory :
        0-3     : Directory length (int)
        4-5     : Number of entries
        6-9     :
    Tag Structure :
        0-1     : Tag id
        2-3     : Tag format
        4-7     : Tag length


"""

class ExifJPEG:
    _tags = {}
    debug = True
    _pointer = 2
    _ptr = 0

    def __init__(self, f):
        self._file = f
        Tools.debug(self.debug, 'JPEG Exif Extraction')

        # Set pointer to the third bit since the two first ones have already been read
        f.seek(self._pointer)

        """
        Read the 10 next bytes as followed :
        - [0-2]     Section declaration
        - [2-4]     Section length
        - [4-8]     Section header name
        - [8-10]    Zero bytes
        """
        marker = f.read(10)
        self._pointer += 10
        while marker[0] == 0xFF and marker[4:8] != b'Exif':
            # While not Exif section, jump to next section
            Tools.debug( self.debug, Tools.decode( marker[0:2] ) )
            # Read block length
            length = Tools.bytes_to_int( marker[2:4] )
            Tools.debug( self.debug, length )

            # Move to section end
            # 6 is Section declaration + Section length
            self._pointer += length + 6
            f.seek(self._pointer)
            # Read next section head
            marker = f.read(10)

        # Get Exif section length
        length = Tools.bytes_to_int( marker[2:4] )
        Tools.debug( self.debug, 'Exif length'.ljust(20, ' ') + ': ' + str(length) )
        #length = Tools.dataread('h', marker[2:4])[0]
        #Tools.debug( self.debug, 'Exif length'.ljust(20, ' ') + ': ' + str(length) )
        # Get endian-ness
        self._endian = Tools.decode( f.read(2) )
        Tools.debug(self.debug, 'Endian : ' + str(self._endian) )

        # Save start of IFD
        self._ifdstart = self._pointer
        
        # Move pointer next to endian-ness + 2 zero-bytes
        self._pointer += 4
        f.seek(self._pointer)
        
        ifdoffset = Tools.dataread('I', f.read(4), self._endian)[0]
        self._pointer += 4
        if ifdoffset != 8:
            # 0th IFD is not right next to TIFF header
            self._pointer = ifdoffset

        self.nextifd(f)

    def nextifd(self, f):
        Tools.debug(self.debug, '===========================')
        Tools.debug(self.debug, '= IFD')
        Tools.debug(self.debug, '===========================')

        print('IFD @ : ' + str(self._pointer))
        f.seek(self._pointer)
        
        #dirlen = Tools.dataread('I', f.read(4), self._endian)[0]
        entries = Tools.dataread('h', f.read(2), self._endian)[0]
        #pointer_stop = self._pointer + dirlen
        self._pointer += 2

        #Tools.debug(self.debug, 'Directory start : ' + str(dirlen))
        #Tools.debug(self.debug, 'Directory size : ' + str(dirlen))
        Tools.debug(self.debug, 'Entries count : ' + str(entries))
        #Tools.debug(self.debug, 'Directory stop : ' + str(pointer_stop))

        #while self._pointer < pointer_stop:
        for i in range(entries):
            self.readtag(f)

        if 0x8769 in self._tags.keys():
            self._pointer = self._tags[0x8769]
            print('Next IFD @ : ' + str(self._pointer))
            f.seek(self._pointer)
            self.nextifd(f)


    def readtag(self, f):
        tagid = Tools.dataread('H', f.read(2), self._endian)[0]
        tagdefault = ('Tag {}'.format(tagid),)
        tagformat = Tools.dataread('h', f.read(2), self._endian)[0]
        taglen = Tools.dataread('I', f.read(4), self._endian)[0]
        tagoffset = Tools.dataread('I', f.read(4), self._endian)[0]

        Tools.debug(self.debug, '---------------------------')
        Tools.debug(self.debug, '- Tag')
        Tools.debug(self.debug, '---------------------------')
        Tools.debug(self.debug, 'Tag id : ' + EXIF_TAGS.get(tagid, tagdefault)[0] )
        Tools.debug(self.debug, 'Tag format : ' + str( tagformat) )
        Tools.debug(self.debug, 'Tag length : ' + str( taglen ) )
        Tools.debug(self.debug, 'Tag offset : ' + str( tagoffset ) )

        f.seek(self._ifdstart + tagoffset)
        typelen = FIELD_TYPES[tagformat][0]
        ##print('Type length : ' + str(typelen * taglen))
        tagdata = self.readtagvalue(f, tagformat, taglen )
        Tools.debug(self.debug, EXIF_TAGS.get(tagid, tagdefault)[0].ljust(20, ' ') + ' : ' + str( tagdata ) )
        self._tags[tagid] = tagdata
        ##print('Tag value : ' + str(tagdata))
        #tagdata = Tools.dataread('c*', tagdata, self._endian)
        #print(tagdata)
        #tagdata = f.read( Tools.dataread('I', taglen, self._endian)[0] )
        #Tools.debug(self.debug, 'Tag data : ' + str( tagdata ) )
        #Tools.debug(self.debug, 'Tag data : ' + str( Tools.dataread('b*', taglen, self._endian)[0] ) )

        self._pointer += 12
        f.seek(self._pointer)

    def readtagvalue(self, f, format, len):
        if format == 2:
            return self.readascii(f)
        else:
            return Tools.dataread(FIELD_TYPES[format][3], f.read( len * FIELD_TYPES[format][0] ), self._endian)[0]

    def readascii(self, f):
        """ Read ascii string until null character """
        value = ''
        c = f.read(1)
        while c != b'\x00':
            value += Tools.dataread('c', c, self._endian)[0].decode('utf-8')
            c = f.read(1)

        return value



class Tools:

    @classmethod
    def dataread(self, format, data, endian=None):
        if endian == b'II':
            format = '<' + format
        elif endian == b'MM':
            format = '>' + format

        return unpack_from(format, data)

    @classmethod
    def bytes_to_hex(self, bytestring):
        return binascii.hexlify( bytearray(bytestring) )

    @classmethod
    def bytes_to_int(self, bytestring):
        hexstring = binascii.hexlify( bytearray(bytestring) )
        return int(hexstring, 16)

    @classmethod
    def decode(self, bytestring):
        """ Decode byte array to human readable string """
        hex_string = binascii.hexlify( bytearray(bytestring) )
        return binascii.unhexlify( hex_string )

    def ByteToHex( byteStr ):
        """
        Convert a byte string to it's hex string representation e.g. for output.
        """
        
        # Uses list comprehension which is a fractionally faster implementation than
        # the alternative, more readable, implementation below
        #   
        #    hex = []
        #    for aChar in byteStr:
        #        hex.append( "%02X " % ord( aChar ) )
        #
        #    return ''.join( hex ).strip()        

        return ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()

    @classmethod
    def debug(self, debug, message):
        """ Print short debug message """
        if debug == True:
            print( message )