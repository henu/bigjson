class Object:

    def __init__(self, reader, read_all):
        self.reader = reader
        self.begin_pos = self.reader._tell_read_pos()
        self.length = -1

        if not read_all:
            return

        self._read_all()

    def _read_all(self):
        """ Reads and validates all bytes in
        the Object. Also counts its length.
        """
        self.length = 0

        self.reader._seek(self.begin_pos)

        if not self.reader._skip_if_next('{'):
            raise Exception('Missing "{"!')

        self.reader._skip_whitespace()

        if self.reader._skip_if_next('}'):
            return

        while True:
            # Skip key. Reading all is not required, because strings
            # are read fully anyway, and if it is not string, then
            # there is an error and reading can be canceled.
            key = self.reader.read(read_all=False)
            if not isinstance(key, basestring):
                raise Exception('Invalid key type in JSON object!')

            # Skip colon and whitespace around it
            self.reader._skip_whitespace()
            if not self.reader._skip_if_next(':'):
                raise Exception('Missing ":"!')
            self.reader._skip_whitespace()

            # Skip value
            self.reader.read(read_all=True)

            self.length += 1

            # Read comma or "}" and whitespace around it.
            self.reader._skip_whitespace()
            if self.reader._skip_if_next(','):
                self.reader._skip_whitespace()
            elif self.reader._skip_if_next('}'):
                break
            else:
                raise Exception('Expected "," or "}"!')

    def __getitem__(self, key):

        if not isinstance(key, basestring):
            raise TypeError(u'Key must be string!')

        # TODO: Use some kind of lookup table!

        # Rewind to requested element from the beginning
        self.reader._seek(self.begin_pos)
        if not self.reader._skip_if_next('{'):
            raise Exception('Missing "{"!')
        self.reader._skip_whitespace()

        if self.reader._is_next('}'):
            raise KeyError('Key not found!')

        while True:
            key2 = self.reader.read(read_all=False)
            if not isinstance(key2, basestring):
                raise Exception('Invalid key type in JSON object!')

            # Read colon
            self.reader._skip_whitespace()
            if not self.reader._skip_if_next(':'):
                raise Exception('Missing ":"!')
            self.reader._skip_whitespace()

            # Read value and return it if the key matches.
            value = self.reader.read(read_all=True)
            if key2 == key:
                return value

            # Skip comma and whitespace around it
            self.reader._skip_whitespace()
            if self.reader._skip_if_next(','):
                self.reader._skip_whitespace()
            elif self.reader._is_next('}'):
                raise KeyError('Key not found!')
            else:
                raise Exception('Expected "," or "}"!')

    def __len__(self):
        if self.length < 0:
            self._read_all()
        return self.length
