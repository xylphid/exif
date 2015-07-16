from Exif.jpeg import ExifJPEG, Tools
from Exif.tags import exif

class Exif:
    debug = True
    _types = {
        'TIFF' : 0,
        'JPEG' : 1
    }

    def __init__(self, filename):
        """ Open file and search for exif tags """

        Tools.debug( self.debug, filename )
        f = open(str(filename), 'rb')
        self.type = self.file_type(f)
        f.close()

    def file_type(self, f):
        """
        Return file type in [TIFF, JPEG]
        """
        soi = f.read(4)
        if soi[0:4] == [b'II*\x00', b'MM\x00*']:
            # TIFF Image file
            return self.type['TIFF']
        elif soi[0:2] == b'\xFF\xD8':
            # JPEG Image file
            ExifJPEG(f)
            return self._types['JPEG']
        else:
            print('Exif not available')

if __name__ == '__main__':
    Exif('C:\\Users\\Anthony\\Pictures\\De Xylphid WPhone\\Pellicule\\2013.05.09 - Ardennes - Lille - Bruges\\IMG_20130510_183306.jpg')
    #Exif('C:\\Users\\Anthony\\Pictures\\De Xylphid WPhone\\Pellicule\\WP_20150706_004.jpg')