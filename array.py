class Array:

    def __init__(self, reader, read_all):
        self.reader = reader
        self.begin_pos = self.reader._tell_read_pos()
        self.length = -1

        # For optimizing index queries
        self.last_known_pos = 0
        self.last_known_pos_index = 0

        if not read_all:
            return

        self._read_all()

    def _read_all(self):
        """ Reads and validates all bytes in
        the Array. Also counts its length.
        """
        self.length = 0

        self.reader._seek(self.begin_pos)

        if not self.reader._skip_if_next('['):
            raise Exception('Missing "["!')

        self.reader._skip_whitespace()

        if self.reader._skip_if_next(']'):
            return

        while True:
            # Skip element
            self.reader.read(read_all=True)

            self.length += 1

            # Skip comma or "]" and whitespace around it
            self.reader._skip_whitespace()
            if self.reader._skip_if_next(','):
                self.reader._skip_whitespace()
            elif self.reader._skip_if_next(']'):
                break
            else:
                raise Exception('Expected "," or "]"!')

    def __getitem__(self, index):
        # TODO: Support negative indexes!

        # TODO: Use some kind of lookup table!

        # Find best known position to rewind to requested index
        if index >= self.last_known_pos_index:
            seek_index = self.last_known_pos_index
            seek_pos = self.last_known_pos
        else:
            seek_index = 0
            seek_pos = 0

        self.reader._seek(seek_pos)
        if seek_index == 0 and not self.reader._skip_if_next('['):
            raise Exception('Missing "["!')
        self.reader._skip_whitespace()

        if self.reader._is_next(']'):
            raise IndexError('Out of range!')

        while True:
            # If this is the requested element, then it doesn't
            # need to be read fully. If not, then its bytes
            # should be skipped, and it needs to be fully read.
            if index == seek_index:
                return self.reader.read(read_all=False)
            else:
                self.reader.read(read_all=True)

            # Skip comma and whitespace around it
            self.reader._skip_whitespace()
            if self.reader._skip_if_next(','):
                self.reader._skip_whitespace()
            elif self.reader._is_next(']'):
                raise IndexError('Out of range!')
            else:
                raise Exception('Expected "," or "]"!')

            seek_index += 1

            if seek_index > self.last_known_pos_index:
                self.last_known_pos_index = seek_index
                self.last_known_pos = self.reader._tell_read_pos()

    def __len__(self):
        if self.length < 0:
            self._read_all()
        return self.length
