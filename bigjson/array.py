class Array:

    _MAX_INDEX_LOOKUP_LENGTH = 1000

    def __init__(self, reader, read_all):
        self.reader = reader
        self.begin_pos = self.reader._tell_read_pos()
        self.length = -1

        # For optimizing index queries
        self.last_known_pos = self.reader._tell_read_pos()
        self.last_known_pos_index = 0
        self.index_lookup = []
        self.index_lookup_multiplier = 1

        if not read_all:
            return

        self._read_all()

    def to_python(self):
        self.reader._seek(self.begin_pos)
        return self._read_all(to_python=True)

    def _read_all(self, to_python=False):
        """ Reads and validates all bytes in
        the Array. Also counts its length.

        If 'to_python' is set to true, then returns list.
        """
        if to_python:
            python_list = []
        else:
            python_list = None

        self.length = 0

        self.reader._seek(self.begin_pos)

        if not self.reader._skip_if_next('['):
            raise Exception(u'Missing "["!')

        self.reader._skip_whitespace()

        if self.reader._skip_if_next(']'):
            return python_list

        while True:
            # Skip or read element
            if to_python:
                python_list.append(self.reader.read(read_all=True, to_python=True))
            else:
                self.reader.read(read_all=True)

            self.length += 1

            # Skip comma or "]" and whitespace around it
            self.reader._skip_whitespace()
            if self.reader._skip_if_next(','):
                self.reader._skip_whitespace()
            elif self.reader._skip_if_next(']'):
                break
            else:
                raise Exception(u'Expected "," or "]"!')

        return python_list

    def __getitem__(self, index):
        # TODO: Support negative indexes!

        # Find best known position to rewind to requested index.
        # First try the last known position
        if index >= self.last_known_pos_index:
            seek_index = self.last_known_pos_index
            seek_pos = self.last_known_pos

        # Last known position was too big. If
        # there is no lookup table or index is
        # too small, then start from beginning.
        elif not self.index_lookup or index < self.index_lookup_multiplier:
            seek_index = 0
            seek_pos = self.begin_pos

        # Try from lookup table
        else:
            lookup_table_index = (index - self.index_lookup_multiplier) // self.index_lookup_multiplier
            # Lookup table index should always be small enough,
            # because if too big indices are requested, then
            # last_known_pos kicks in at the start.
            assert lookup_table_index < len(self.index_lookup)
            seek_index = (lookup_table_index + 1) * self.index_lookup_multiplier
            seek_pos = self.index_lookup[lookup_table_index]

        self.reader._seek(seek_pos)
        if seek_index == 0 and not self.reader._skip_if_next('['):
            raise Exception(u'Missing "["!')
        self.reader._skip_whitespace()

        if self.reader._is_next(']'):
            raise IndexError(u'Out of range!')

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
                raise IndexError(u'Out of range!')
            else:
                raise Exception(u'Expected "," or "]"!')

            seek_index += 1

            # Update lookup variables
            if seek_index > self.last_known_pos_index:
                self.last_known_pos_index = seek_index
                self.last_known_pos = self.reader._tell_read_pos()
            if seek_index == (len(self.index_lookup) + 1) * self.index_lookup_multiplier:
                self.index_lookup.append(self.reader._tell_read_pos())
                # If lookup table grows too big, half of its members will be removed
                if len(self.index_lookup) > Array._MAX_INDEX_LOOKUP_LENGTH:
                    self.index_lookup = [pos for i, pos in enumerate(self.index_lookup) if i % 2 == 1]
                    self.index_lookup_multiplier *= 2

    def __len__(self):
        if self.length < 0:
            self._read_all()
        return self.length
