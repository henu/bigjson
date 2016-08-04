class Array:

    def __init__(self, reader, read_all):
        self.reader = reader
        self.begin_pos = self.reader._tell_read_pos()
        self.length = -1

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

        # Rewind to requested element from the beginning
        self.reader._seek(self.begin_pos)
        if not self.reader._skip_if_next('['):
            raise Exception('Missing "["!')
        self.reader._skip_whitespace()

        if self.reader._is_next(']'):
            raise IndexError('Out of range!')

        while True:
            element = self.reader.read(read_all=True)

            if index == 0:
                return element

            # Skip comma and whitespace around it
            self.reader._skip_whitespace()
            if self.reader._skip_if_next(','):
                self.reader._skip_whitespace()
            elif self.reader._is_next(']'):
                raise IndexError('Out of range!')
            else:
                raise Exception('Expected "," or "]"!')

            index -= 1

    def __len__(self):
        if self.length < 0:
            self._read_all()
        return self.length
