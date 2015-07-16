from Exif.exception import *
from Exif.jpeg import ExifJPEG
from Exif.utils import *
from Exif.tags import exif
import sys

class Exif:
    debug = True
    _types = {
        'TIFF' : 0,
        'JPEG' : 1
    }

    def __init__(self, filename, autoprocess=True):
        """
        Register filename and process if available
        """

        ExifTools.debug( self.debug, filename )
        self._filename = filename
        if autoprocess:
            self.process_file()

    def process_file(self):
        """
        Open file and search for exif tags
        """
        f = open(str(self._filename), 'rb')
        self.type = self.get_file_type(f)
        f.close()
        

    def get_file_type(self, f):
        """
        Return file type in [TIFF, JPEG]
        """
        soi = f.read(4)
        try:
            if soi[0:4] == [b'II*\x00', b'MM\x00*']:
                # TIFF Image file
                return self._types['TIFF']
            elif soi[0:2] == b'\xFF\xD8':
                # JPEG Image file
                ExifJPEG(f)
                return self._types['JPEG']
            else:
                print('Exif not available')
        except ExifTypeNotAvailable as e:
            sys.stderr.write( e.parameter )

if __name__ == '__main__':
    #Exif('C:\\Users\\Anthony\\Pictures\\De Xylphid WPhone\\Pellicule\\2013.05.09 - Ardennes - Lille - Bruges\\IMG_20130510_183306.jpg')
    Exif('C:\\Users\\Anthony\\Pictures\\De Xylphid WPhone\\Pellicule\\WP_20150706_004.jpg', autoprocess=True)