from .exif import *
from .types import *
from Exif.exception import *

import logging

class Tag:
    """
    Tag objet containing all informations usefull for display and writting
    """

    def __init__(self, name, value, etype):
        try:
            if not FIELD_TYPES[etype]:
                raise ExifTagTypeError( etype )

            self._name = name
            self.value = value
            self.type = etype
        except ExifTagTypeError as e:
            logging.info( e )

    def len(self):
        if self.type == 2:
            return len(self.value) + 1
        else:
            return len(self.value)

    def __str__(self):
        if (self.type == 1):
            return repr(self.value.decode('utf-8'))
        else:
            return repr(self.value)