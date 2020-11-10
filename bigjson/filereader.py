from .array import Array
from .obj import Object


class FileReader:

    _WHITESPACE = b'\t\n\r '
    _READBUF_CHUNK_SIZE = 1024*1024

    def __init__(self, file, encoding):
        self.file = file
        # TODO: Support encodings where basic shortest characters are longer than one byte (e.g. UTF-16 and UTF-32)!
        self.encoding = encoding

        # This buffer is for reading and peeking
        self.readbuf = b''
        self.readbuf_read = 0
        self.readbuf_pos = 0

    def read(self, read_all=False, to_python=False):
        # "to_python" cannot be set without "read_all"
        assert read_all or not to_python

        self._skip_whitespace()

        # None
        if self._skip_if_next('null'):
            return None

        # False
        if self._skip_if_next('false'):
            return False

        # True
        if self._skip_if_next('true'):
            return True

        # Number
        if self._peek() in b'-0123456789':
            num = self._get()
            # Check sign
            if num == b'-':
                num += self._get()
            # Read integer part
            if num[-1] != b'0':
                while self._peek() in b'0123456789':
                    num += self._get()
            # Read possible decimal part and convert to float
            if self._peek() == b'.':
                self._get()
                num += b'.' + self._get()
                if num[-1] not in b'01234567890':
                    raise Exception(u'Expected digit after dot! Position {}'.format(self.readbuf_read))
                while self._peek() in b'0123456789':
                    num += self._get()
                num = float(num)
            else:
                num = int(num)
            # Read possible exponent
            if self._peek() in b'eE':
                self._get()
                exp = self._get()
                exp_neg = False
                if exp == b'-':
                    exp_neg = True
                    exp = self._get()
                elif exp == b'+':
                    exp = self._get()
                while self._peek() in b'0123456789':
                    exp += self._get()
                exp = int(exp)
                exp = 10 ** exp
                if exp_neg:
                    num = float(num) / exp
                else:
                    num *= exp
            return num

        # String
        if self._skip_if_next('"'):
            string = b''

            while True:
                c = self._get()

                if c == b'"':
                    break

                if c == b'\\':
                    c = self._get()
                    if c == b'"':
                        string += b'"'
                    elif c == b'\\':
                        string += b'\\'
                    elif c == b'/':
                        string += b'/'
                    elif c == b'b':
                        string += b'\b'
                    elif c == b'f':
                        string += b'\f'
                    elif c == b'n':
                        string += b'\n'
                    elif c == b'r':
                        string += b'\r'
                    elif c == b't':
                        string += b'\t'
                    elif c == b'u':
                        unicode_bytes = self._read(4)
                        string += (b'\\u' + unicode_bytes).decode('unicode_escape').encode(self.encoding)
                    else:
                        raise Exception(u'Unexpected \\{} in backslash encoding! Position {}'.format(c.decode('utf-8'), self.readbuf_read - 1))

                else:
                    string += c

            return string.decode(self.encoding)

        # Array
        if self._peek() == b'[':
            if to_python:
                array = Array(self, False)
                return array.to_python()
            else:
                return Array(self, read_all)

        # Object
        if self._peek() == b'{':
            if to_python:
                obj = Object(self, False)
                return obj.to_python()
            else:
                return Object(self, read_all)

        c = self._peek()

        raise Exception(u'Unexpected bytes! Value \'{}\' Position {}'.format(c.decode('utf-8'), self.readbuf_read))

    def _skip_whitespace(self):
        while True:
            next_char = self._peek()
            if next_char is None:
                break

            if next_char not in FileReader._WHITESPACE:
                break

            self._get()

    def _get(self):
        self._ensure_readbuf_left(1)
        if len(self.readbuf) - self.readbuf_read < 1:
            raise Exception(u'Unexpected end of file when getting next byte!')
        result = self.readbuf[self.readbuf_read:self.readbuf_read + 1]
        self.readbuf_read += 1
        return result

    def _read(self, amount):
        self._ensure_readbuf_left(amount)
        if len(self.readbuf) - self.readbuf_read < amount:
            raise Exception(u'Unexpected end of file reading a chunk!')
        result = self.readbuf[self.readbuf_read:self.readbuf_read + amount]
        self.readbuf_read += amount
        return result

    def _peek(self):
        self._ensure_readbuf_left(1)
        if len(self.readbuf) - self.readbuf_read < 1:
            return None
        return self.readbuf[self.readbuf_read:self.readbuf_read + 1]

    def _is_next(self, s):
        if not isinstance(s, bytes):
            s = s.encode(self.encoding)
        s_len = len(s)
        self._ensure_readbuf_left(s_len)
        if len(self.readbuf) - self.readbuf_read < s_len:
            return False
        return self.readbuf[self.readbuf_read:self.readbuf_read + s_len] == s

    def _skip_if_next(self, s):
        """ If next bytes are same as in 's', then skip them and return True.
        """
        if not isinstance(s, bytes):
            s = s.encode(self.encoding)
        if self._is_next(s):
            self.readbuf_read += len(s)
            return True
        return False

    def _ensure_readbuf_left(self, minimum_left):
        if len(self.readbuf) - self.readbuf_read >= minimum_left:
            return
        read_amount = max(minimum_left, FileReader._READBUF_CHUNK_SIZE) - (len(self.readbuf) - self.readbuf_read)
        self.readbuf_pos += self.readbuf_read
        old_pos = self.file.tell()
        self.readbuf = self.readbuf[self.readbuf_read:] + self.file.read(read_amount)
        self.readbuf_read = 0

    def _tell_read_pos(self):
        return self.readbuf_pos + self.readbuf_read

    def _seek(self, pos):
        # If position is at the area of
        # readbuffer, then just rewind it.
        if pos >= self.readbuf_pos and pos < self.readbuf_pos + len(self.readbuf):
            self.readbuf_read = pos - self.readbuf_pos
        # If position is outside the readbuffer,
        # then read buffer from scratch
        else:
            self.readbuf = b''
            self.readbuf_read = 0
            self.readbuf_pos = pos
            self.file.seek(pos)
