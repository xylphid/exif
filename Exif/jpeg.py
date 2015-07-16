from .tags import *
from .utils import *

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

    def __init__(self, f):
        self._file = f
        debug(self.debug, 'JPEG Exif Extraction')

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
            debug( self.debug, decode( marker[0:2] ) )
            # Read block length
            length = unpack_datas('>H', marker[2:4])[0]
            debug( self.debug, length )

            # Move to section end
            # 6 is Section declaration + Section length
            self._pointer += length + 6
            f.seek(self._pointer)
            # Read next section head
            marker = f.read(10)

        # Get Exif section length
        length = unpack_datas('>H', marker[2:4])[0]
        # Get endian-ness
        self._endian = decode( f.read(2) )
        f.seek(f.tell() - 4)

        # Save start of IFD
        self._ifdstart = self._pointer
        
        # Move pointer next to endian-ness + 2 zero-bytes
        self._pointer += 4
        f.seek(self._pointer)
        
        ifdoffset = unpack_datas('I', f.read(4), self._endian)[0]
        self._pointer += 4
        if ifdoffset != 8:
            # 0th IFD is not right next to TIFF header
            self._pointer = ifdoffset

        self.nextifd(f)

        # Display tags
        debug(self.debug, '===========================')
        debug(self.debug, '= Tags')
        debug(self.debug, '===========================')
        for key, val in self._tags.items():
            tagdefault = ('Tag {}'.format(key),)
            debug(self.debug, EXIF_TAGS.get(key, tagdefault)[0].ljust(25, ' ') + ' : ' + str( val ) )

    def nextifd(self, f):
        """
        Read the next IFD at the current pointer position
        """

        f.seek(self._pointer)
        entries = unpack_datas('h', f.read(2), self._endian)[0]
        self._pointer += 2

        for i in range(entries):
            self.readtag(f, i+1)

        if 0x8769 in self._tags.keys():
            self._pointer = self._ifdstart + self._tags[0x8769]
            del self._tags[0x8769]
            f.seek(self._pointer)
            self.nextifd(f)


    def readtag(self, f, i):
        tagid = unpack_datas('H', f.read(2), self._endian)[0]
        tagdefault = ('Tag {}'.format(tagid),)
        tagformat = unpack_datas('h', f.read(2), self._endian)[0]
        taglen = unpack_datas('I', f.read(4), self._endian)[0]

        if taglen * FIELD_TYPES[tagformat][0] > 4:
            tagoffset = unpack_datas('I', f.read(4), self._endian)[0]
            f.seek(self._ifdstart + tagoffset)
                    
        #if EXIF_TAGS.get(tagid, tagdefault)[0] == 'NOrientation':
        if not 1:
            debug(self.debug, '---------------------------')
            debug(self.debug, '- Tag ' + str(i))
            debug(self.debug, '---------------------------')
            debug(self.debug, 'Tag id : ' + EXIF_TAGS.get(tagid, tagdefault)[0] )
            debug(self.debug, 'Tag format : ' + str( tagformat ) )
            debug(self.debug, 'Tag length : ' + str( taglen ) )
        #if EXIF_TAGS.get(tagid, tagdefault)[0] == 'NOrientation':
        if EXIF_TAGS.get(tagid, tagdefault)[0] == 'NOrientation':
            debug(self.debug, '---------------------------')

        tagdata = self.readtagvalue(f, tagformat, taglen )
        self._tags[tagid] = tagdata

        self._pointer += 12
        f.seek(self._pointer)

    def readtagvalue(self, f, format, length):
        if format == 2:
            # Read string value
            return self.readascii(f)
        elif format in (5, 10):
            # Read ratio value
            return Ratio(
                    unpack_datas(FIELD_TYPES[format][3], f.read(4), self._endian)[0],
                    unpack_datas(FIELD_TYPES[format][3], f.read(4), self._endian)[0]
                )
        else:
            return unpack_datas(FIELD_TYPES[format][3], f.read( length * FIELD_TYPES[format][0] ), self._endian)[0]

    def readascii(self, f):
        """ Read ascii string until null character """
        value = ''
        c = f.read(1)
        while c != b'\x00':
            value += unpack_datas('c', c, self._endian)[0].decode('utf-8')
            c = f.read(1)

        return value
