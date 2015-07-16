import binascii
from struct import unpack_from

def unpack_datas(format, data, endian=None):
    # Unpack datas accroding to the specified format and endian-ness
    if endian == b'II':
        format = '<' + format
    elif endian == b'MM':
        format = '>' + format

    return unpack_from(format, data)

def decode(bytestring):
    # Decode byte array to human readable string
    hex_string = binascii.hexlify( bytearray(bytestring) )
    
    return binascii.unhexlify( hex_string )

def debug(debug, message):
    """ Print short debug message """
    if debug == True:
        print( message )

class Ratio:
    """
    Ratio object that eventually will be able to reduce itself to lowest
    common denominator for printing.
    """

    def __init__(self, num, den):
        self.num = num
        self.den = den

    def __repr__(self):
        self.reduce()
        if self.den == 1:
            return str(self.num)
        return '%d/%d' % (self.num, self.den)

    def _gcd(self, a, b):
        if b == 0:
            return a
        else:
            return self._gcd(b, a % b)

    def reduce(self):
        div = self._gcd(self.num, self.den)
        if div > 1:
            self.num = self.num // div
            self.den = self.den // div

class ExifTools:
    """
    Exif tools to read datas
    """
    @classmethod
    def unpack_datas(self, format, data, endian=None):
        # Unpack datas accroding to the specified format and endian-ness
        if endian == b'II':
            format = '<' + format
        elif endian == b'MM':
            format = '>' + format

        return unpack_from(format, data)

    @classmethod
    def decode(self, bytestring):
        # Decode byte array to human readable string
        hex_string = binascii.hexlify( bytearray(bytestring) )

        return binascii.unhexlify( hex_string )

    @classmethod
    def debug(self, debug, message):
        """ Print short debug message """
        if debug == True:
            print( message )