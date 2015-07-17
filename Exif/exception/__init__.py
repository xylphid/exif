class ExifTypeError(Exception):
    def __init__(self, value):
        self.value = value

    def __str_(self):
        return repr(self.value)

class ExifTagTypeError(Exception):
    def __init__(self, value):
        self.value = value
        self.message = 'Tag type ({0}) is unknown.'.format(self.value)

    def __str__(self):
        return repr(self.message)