from .tags import *
from .utils import *

import logging

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
        logging.debug( 'JPEG Exif Extraction' )

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
            # ###
            # Read block length
            length = unpack_datas('>H', marker[2:4])[0]

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
        print( '===========================')
        print( '= Tags')
        print( '===========================')
        for key, tag in self._tags.items():
            #tagdefault = ('Tag {}'.format(key),)
            print( tag._name.ljust(25, ' ') + ' : ' + repr(tag.value) )
            #print( EXIF_TAGS.get(key, tagdefault)[0].ljust(25, ' ') + ' : ' + str( tag ) )

    def nextifd(self, f, tag_dict=EXIF_TAGS):
        """
        Read the next IFD at the current pointer position
        """

        f.seek(self._pointer)
        entries = unpack_datas('H', f.read(2), self._endian)[0]
        #logging.debug( 'IFD entries : ' + str(entries))
        self._pointer += 2

        for i in range(entries):
            self.readtag(f, i+1, tag_dict)

        if 0x8769 in self._tags.keys():
            #self._pointer = self._ifdstart + self._tags[0x8769]
            self._pointer = self._ifdstart + self._tags[0x8769].value
            del self._tags[0x8769]
            f.seek(self._pointer)
            self.nextifd(f)


    def readtag(self, f, i, tag_dict, tag_prefix=None):
        # Read tag infos [id, format, len, datas]
        tagid = unpack_datas('H', f.read(2), self._endian)[0]
        tagdefault = ('Tag {}'.format(tagid),)
        # Get tag name or set default 
        tagname = 'Tag {}'.format(tagid) if not tag_dict.get(tagid) else tag_dict.get(tagid)[0]

        tagformat = unpack_datas('h', f.read(2), self._endian)[0]
        taglen = unpack_datas('I', f.read(4), self._endian)[0]

        if taglen * FIELD_TYPES[tagformat][0] > 4:
            # If taglen > 4 then it is a pointer to the tag value
            tagoffset = unpack_datas('I', f.read(4), self._endian)[0]
            f.seek(self._ifdstart + tagoffset)


        # Read tag value and populate dictionnary
        tagdata = self.readtagvalue(f, tagformat, taglen )
        self._tags[tagid] = Tag(tagname, tagdata, tagformat)
        #self._tags[tagid] = tagdata
        
        """
        logging.debug( 'Tag id : ' + str(tagid) )
        logging.debug( 'Tag format : ' + str(tagformat) )
        logging.debug( 'Tag length : ' + str(taglen) )
        logging.debug('Tagname : %s', tagname )
        """
        #if EXIF_TAGS.get(tagid, tagdefault)[0] == 'NOrientation':
        if not 1:
            print( '---------------------------')
            print( '- Tag ' + str(i))
            print( '---------------------------')
            print( 'Tag id : ' + str(tagid) )
            print( 'Tag id : ' + tag_dict.get(tagid, tagdefault)[0] )
            print( 'Tag format : ' + str( tagformat ) )
            print( 'Tag length : ' + str( taglen ) )
        

        if not 1:
            print( 'Tag data : ' + str(tagdata) )
            print( '---------------------------')

        tagentry = tag_dict.get(tagid)
        if tagentry and len(tagentry) != 1:
            if callable(tagentry[1]):
                self._tags[tagid].value = tagentry[1](tagdata)
            elif type(tagentry[1]) is tuple:
                # If tag entry is tuple, then read sub IFD
                current_pointer = self._pointer
                self._pointer = self._ifdstart + tagdata
                self.nextifd(f, tagentry[1][1])
                self._pointer = current_pointer
            else:
                self._tags[tagid].value = tagentry[1].get(tagdata)

        self._pointer += 12
        f.seek(self._pointer)

    def readtagvalue(self, f, format, length):
        # Read tag value according to format parameter
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
        # Read ascii string until null character
        value = ''
        c = f.read(1)
        while c != b'\x00':
            value += unpack_datas('c', c, self._endian)[0].decode('utf-8')
            c = f.read(1)

        return value
