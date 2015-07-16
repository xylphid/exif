class ExifTypeNotAvailable(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str_(self):
        return repr(self.parameter)