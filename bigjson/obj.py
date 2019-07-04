import sys


if sys.version[0] == '2':
    string_types = basestring
else:
    string_types = str


class Object:

    _GET_METHOD_RAISE_EXCEPTION = 0
    _GET_METHOD_RETURN_DEFAULT = 1
    _GET_METHOD_RETURN_BOOLEAN = 2

    def __init__(self, reader, read_all):
        self.reader = reader
        self.begin_pos = self.reader._tell_read_pos()
        self.length = -1

        if not read_all:
            return

        self._read_all()

    def keys(self):
        return [keyvalue[0] for keyvalue in self.iteritems()]

    def values(self):
        return [keyvalue[1] for keyvalue in self.iteritems()]

    def items(self):
        return [keyvalue for keyvalue in self.iteritems()]

    def iteritems(self):
        self.reader._seek(self.begin_pos)

        if not self.reader._skip_if_next('{'):
            raise Exception(u'Missing "{"!')

        self.reader._skip_whitespace()

        if self.reader._skip_if_next('}'):
            return

        while True:
            # Read key. Reading all is not required, because strings
            # are read fully anyway, and if it is not string, then
            # there is an error and reading can be canceled.
            key = self.reader.read(read_all=False)
            if not isinstance(key, string_types):
                raise Exception(u'Invalid key type in JSON object!')

            # Skip colon and whitespace around it
            self.reader._skip_whitespace()
            if not self.reader._skip_if_next(':'):
                raise Exception(u'Missing ":"!')
            self.reader._skip_whitespace()

            # Read value
            value = self.reader.read(read_all=True)

            yield (key, value)

            # Read comma or "}" and whitespace around it.
            self.reader._skip_whitespace()
            if self.reader._skip_if_next(','):
                self.reader._skip_whitespace()
            elif self.reader._skip_if_next('}'):
                break
            else:
                raise Exception(u'Expected "," or "}"!')

    def get(self, key, default=None):
        return self._get(key, default, Object._GET_METHOD_RETURN_DEFAULT)

    def to_python(self):
        self.reader._seek(self.begin_pos)
        return self._read_all(to_python=True)

    def _read_all(self, to_python=False):
        """ Reads and validates all bytes in
        the Object. Also counts its length.

        If 'to_python' is set to true, then returns dict.
        """
        if to_python:
            python_dict = {}
        else:
            python_dict = None

        self.length = 0

        self.reader._seek(self.begin_pos)

        if not self.reader._skip_if_next('{'):
            raise Exception(u'Missing "{"!')

        self.reader._skip_whitespace()

        if self.reader._skip_if_next('}'):
            return python_dict

        while True:
            # Skip key. Reading all is not required, because strings
            # are read fully anyway, and if it is not string, then
            # there is an error and reading can be canceled.
            key = self.reader.read(read_all=False)
            if not isinstance(key, string_types):
                raise Exception(u'Invalid key type in JSON object!')

            # Skip colon and whitespace around it
            self.reader._skip_whitespace()
            if not self.reader._skip_if_next(':'):
                raise Exception(u'Missing ":"!')
            self.reader._skip_whitespace()

            # Skip or read value
            if to_python:
                python_dict[key] = self.reader.read(read_all=True, to_python=True)
            else:
                self.reader.read(read_all=True)

            self.length += 1

            # Read comma or "}" and whitespace around it.
            self.reader._skip_whitespace()
            if self.reader._skip_if_next(','):
                self.reader._skip_whitespace()
            elif self.reader._skip_if_next('}'):
                break
            else:
                raise Exception(u'Expected "," or "}"!')

        return python_dict

    def __contains__(self, key):
        return self._get(key, None, Object._GET_METHOD_RETURN_BOOLEAN)

    def __getitem__(self, key):
        return self._get(key, None, Object._GET_METHOD_RAISE_EXCEPTION)

    def _get(self, key, default, method):

        if not isinstance(key, string_types):
            raise TypeError(u'Key must be string!')

        # TODO: Use some kind of lookup table!

        # Rewind to requested element from the beginning
        self.reader._seek(self.begin_pos)
        if not self.reader._skip_if_next('{'):
            raise Exception(u'Missing "{"!')
        self.reader._skip_whitespace()

        if self.reader._is_next('}'):
            if method == Object._GET_METHOD_RAISE_EXCEPTION:
                raise KeyError(key)
            elif method == Object._GET_METHOD_RETURN_DEFAULT:
                return None
            else:
                return False

        while True:
            key2 = self.reader.read(read_all=False)
            if not isinstance(key2, string_types):
                raise Exception(u'Invalid key type in JSON object!')

            # Read colon
            self.reader._skip_whitespace()
            if not self.reader._skip_if_next(':'):
                raise Exception(u'Missing ":"!')
            self.reader._skip_whitespace()

            # If this is the requested value, then it doesn't
            # need to be read fully. If not, then its bytes
            # should be skipped, and it needs to be fully read.
            if key2 == key:
                if method == Object._GET_METHOD_RETURN_BOOLEAN:
                    return True
                else:
                    return self.reader.read(read_all=False)
            else:
                self.reader.read(read_all=True)

            # Skip comma and whitespace around it
            self.reader._skip_whitespace()
            if self.reader._skip_if_next(','):
                self.reader._skip_whitespace()
            elif self.reader._is_next('}'):
                if method == Object._GET_METHOD_RAISE_EXCEPTION:
                    raise KeyError(key)
                elif method == Object._GET_METHOD_RETURN_DEFAULT:
                    return None
                else:
                    return False
            else:
                raise Exception(u'Expected "," or "}"!')

    def __len__(self):
        if self.length < 0:
            self._read_all()
        return self.length
