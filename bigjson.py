class BigJSON:

    _WHITESPACE = '\t\n '
    _READBUF_CHUNK_SIZE = 1024*1024

    def __init__(self, file):
        self.file = file

        # This buffer is for reading and peeking
        self.readbuf = ''

        self.root_node = Node(self)

    def __getitem__(self, index):
        return self.root_node[index]

    def _skip_whitespace(self):
        while True:
            # Read whitespace from current readbuffer
            whitespace_in_readbuf = 0
            while whitespace_in_readbuf < len(self.readbuf) and self.readbuf[whitespace_in_readbuf] in BigJSON._WHITESPACE:
                whitespace_in_readbuf += 1
            self.readbuf = self.readbuf[whitespace_in_readbuf:]

            # If readbuffer is not empty, then read more
            if len(self.readbuf) > 0:
                return

            # Readbuffer is empty, so load more
            self._fill_readbuf(BigJSON._READBUF_CHUNK_SIZE)

    def _get(self):
        self._fill_readbuf(1)
        if len(self.readbuf) == 0:
            raise Exception('Unexpected end of file when getting next byte!')
        result = self.readbuf[0]
        self.readbuf = self.readbuf[1:]
        return result

    def _read(self, amount):
        self._fill_readbuf(amount)
        if len(self.readbuf) < amount:
            raise Exception('Unexpected end of file when getting next byte!')
        result = self.readbuf[:amount]
        self.readbuf = self.readbuf[amount:]
        return result

    def _peek(self):
        self._fill_readbuf(1)
        if len(self.readbuf) == 0:
            return None
        return self.readbuf[0]

    def _is_next(self, s):
        self._fill_readbuf(len(s))
        return self.readbuf.startswith(s)

    def _skip_if_next(self, s):
        """ If next bytes are same as in 's', then skip them and return True.
        """
        if self._is_next(s):
            self.readbuf = self.readbuf[len(s):]
            return True
        return False

    def _fill_readbuf(self, desired_size):
        read_amount = desired_size - len(self.readbuf)
        if read_amount <= 0:
            return
        self.readbuf += self.file.read(read_amount)

    def _tell_read_pos(self):
        return self.file.tell() - len(self.readbuf)

    def _seek(self, pos):
        self.readbuf = u''
        self.file.seek(pos)


class Node:

    TYPE_NULL = 0
    TYPE_FALSE = 1
    TYPE_TRUE = 2
    TYPE_NUMBER = 3
    TYPE_STRING = 4
    TYPE_ARRAY = 5
    TYPE_OBJECT = 6

    def __init__(self, bj):
        self.bj = bj

        self.bj._skip_whitespace()

        # Read part of file to analyze type of it
        if self.bj._skip_if_next('null'):
            self.type = Node.TYPE_NULL

        elif self.bj._skip_if_next('false'):
            self.type = Node.TYPE_FALSE

        elif self.bj._skip_if_next('true'):
            self.type = Node.TYPE_TRUE

        elif self.bj._peek() in '-0123456789':
            self.type = Node.TYPE_NUMBER
            num = self.bj._get()
            # Check sign
            if num == '-':
                num += self.bj._get()
            # Read integer part
            if num[-1] != '0':
                while self.bj._peek() in '0123456789':
                    num += self.bj._get()
            # Read possible decimal part and convert to float
            if self.bj._peek() == '.':
                self.bj._get()
                num += '.' + self.bj._get()
                if num[-1] not in '0123456790':
                    raise Exception('Expected digit after dot!')
                while self.bj._peek() in '0123456789':
                    num += self.bj._get()
                self.number = float(num)
            else:
                self.number = int(num)
            # Read possible exponent
            if self.bj._peek() in 'eE':
                self.bj._get()
                exp = self.bj._get()
                exp_neg = False
                if exp == '-':
                    exp_neg = True
                    exp = self.bj._get()
                elif exp == '+':
                    exp = self.bj._get()
                while self.bj._peek() in '0123456789':
                    exp += self.bj._get()
                exp = int(exp)
                exp = 10 ** exp
                if exp_neg:
                    self.number = float(self.number) / exp
                else:
                    self.number *= exp

        elif self.bj._skip_if_next('"'):
            self.type = Node.TYPE_STRING

            self.string = u''

            while True:
                c = self.bj._get()

                if c == u'"':
                    break

                if c == u'\\':
                    c = self.bj._get()
                    if c == u'"':
                        self.string += u'"'
                    elif c == u'\\':
                        self.string += u'\\'
                    elif c == u'/':
                        self.string += u'/'
                    elif c == u'b':
                        self.string += u'\b'
                    elif c == u'f':
                        self.string += u'\f'
                    elif c == u'n':
                        self.string += u'\n'
                    elif c == u'r':
                        self.string += u'\r'
                    elif c == u't':
                        self.string += u'\t'
                    elif c == u'u':
                        unicode_bytes = self.bj._read(4)
                        self.string += ('\\u' + unicode_bytes).decode('unicode_escape')
                    else:
                        raise Exception(u'Unexpected {} in backslash encoding!'.format(c))

                else:
                    self.string += c

        elif self.bj._skip_if_next('['):
            self.type = Node.TYPE_ARRAY
            self.fully_read = False
            # TODO: Replace this single lookup position with some kind of lookup table!
            self.children_begin = self.bj._tell_read_pos()

        elif self.bj._skip_if_next('{'):
            self.type = Node.TYPE_OBJECT
            self.fully_read = False
            # TODO: Replace this single lookup position with some kind of lookup table!
            self.children_begin = self.bj._tell_read_pos()

        else:
            raise Exception('Unexpected bytes!')

    def get_type(self):
        return ['null', 'false', 'true', 'number', 'string', 'array', 'object'][self.type]

    def __getitem__(self, index):
        if self.type == Node.TYPE_ARRAY:

            # TODO: Support negative indexes!

            # Rewind to requested child
            self.bj._seek(self.children_begin)
            self.bj._skip_whitespace()
            while True:
                if self.bj._is_next(']'):
                    raise IndexError('Out of range!')

                child = Node(self.bj)
                child._read_fully()

                if index == 0:
                    return child._get_value()

                # Skip comma and whitespace around it
                self.bj._skip_whitespace()
                if not self.bj._skip_if_next(','):
                    raise IndexError('Out of range!')
                self.bj._skip_whitespace()

                index -= 1

        elif self.type == Node.TYPE_OBJECT:

            if not isinstance(index, basestring):
                raise TypeError(u'Key must be string!')

            # Rewind to requested child
            self.bj._seek(self.children_begin)
            self.bj._skip_whitespace()

            if self.bj._is_next('}'):
                raise KeyError('Key not found!')

            while True:

                # Read key
                key = Node(self.bj)
                if key.type != Node.TYPE_STRING:
                    raise Exception('Invalid key type in JSON!')

                # Read colon
                self.bj._skip_whitespace()
                if not self.bj._skip_if_next(':'):
                    raise Exception('Missing ":"!')
                self.bj._skip_whitespace()

                # Read child and return it if the key matches.
                child = Node(self.bj)
                child._read_fully()
                if key._get_value() == index:
                    return child._get_value()

                # Read comma or "}"
                self.bj._skip_whitespace()
                if self.bj._skip_if_next(','):
                    self.bj._skip_whitespace()
                elif self.bj._is_next('}'):
                    raise KeyError('Key not found!')
                else:
                    raise Exception('Expected "," or "}"!')

        elif self.type == Node.TYPE_STRING:

            return self.string[index]

        else:

            raise Exception('Index operator does not work with type "{}"!'.format(self.get_type))

    def _get_value(self):
        """ If possible, returns basic python object, but
        with complex Nodes, returns the Node itself.
        """
        if self.type == Node.TYPE_NULL:
            return None
        if self.type == Node.TYPE_FALSE:
            return False
        if self.type == Node.TYPE_TRUE:
            return True
        if self.type == Node.TYPE_NUMBER:
            return self.number
        if self.type == Node.TYPE_STRING:
            return self.string
        return self

    def _read_fully(self):

        # If already fully read
        if self.type in [Node.TYPE_NULL, Node.TYPE_FALSE, Node.TYPE_TRUE, Node.TYPE_NUMBER, Node.TYPE_STRING]:
            return

        if self.type == Node.TYPE_ARRAY:

            self.bj._seek(self.children_begin)
            self.bj._skip_whitespace()
            if self.bj._skip_if_next(']'):
                return
            while True:
                child = Node(self.bj)
                child._read_fully()

                # Skip comma and whitespace around it
                self.bj._skip_whitespace()
                if self.bj._skip_if_next(','):
                    self.bj._skip_whitespace()
                elif self.bj._skip_if_next(']'):
                    break
                else:
                    raise Exception('Expected "," or "]"!')

        else:

            self.bj._seek(self.children_begin)
            self.bj._skip_whitespace()

            if self.bj._skip_if_next('}'):
                return

            while True:

                # Read key
                key = Node(self.bj)
                if key.type != Node.TYPE_STRING:
                    raise Exception('Invalid key type in JSON!')

                # Read colon
                self.bj._skip_whitespace()
                if not self.bj._skip_if_next(':'):
                    raise Exception('Missing ":"!')
                self.bj._skip_whitespace()

                # Read child
                child = Node(self.bj)
                child._read_fully()

                # Read comma or "}"
                self.bj._skip_whitespace()
                if self.bj._skip_if_next(','):
                    self.bj._skip_whitespace()
                elif self.bj._skip_if_next('}'):
                    break
                else:
                    raise Exception('Expected "," or "}"!')
