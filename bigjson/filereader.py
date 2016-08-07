from array import Array
from obj import Object


class FileReader:

    _WHITESPACE = '\t\n '
    _READBUF_CHUNK_SIZE = 1024*1024

    def __init__(self, file):
        self.file = file

        # This buffer is for reading and peeking
        self.readbuf = ''
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
        if self._peek() in '-0123456789':
            num = self._get()
            # Check sign
            if num == '-':
                num += self._get()
            # Read integer part
            if num[-1] != '0':
                while self._peek() in '0123456789':
                    num += self._get()
            # Read possible decimal part and convert to float
            if self._peek() == '.':
                self._get()
                num += '.' + self._get()
                if num[-1] not in '01234567890':
                    raise Exception(u'Expected digit after dot!')
                while self._peek() in '0123456789':
                    num += self._get()
                num = float(num)
            else:
                num = int(num)
            # Read possible exponent
            if self._peek() in 'eE':
                self._get()
                exp = self._get()
                exp_neg = False
                if exp == '-':
                    exp_neg = True
                    exp = self._get()
                elif exp == '+':
                    exp = self._get()
                while self._peek() in '0123456789':
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
            string = u''

            while True:
                c = self._get()

                if c == u'"':
                    break

                if c == u'\\':
                    c = self._get()
                    if c == u'"':
                        string += u'"'
                    elif c == u'\\':
                        string += u'\\'
                    elif c == u'/':
                        string += u'/'
                    elif c == u'b':
                        string += u'\b'
                    elif c == u'f':
                        string += u'\f'
                    elif c == u'n':
                        string += u'\n'
                    elif c == u'r':
                        string += u'\r'
                    elif c == u't':
                        string += u'\t'
                    elif c == u'u':
                        unicode_bytes = self._read(4)
                        string += ('\\u' + unicode_bytes).decode('unicode_escape')
                    else:
                        raise Exception(u'Unexpected {} in backslash encoding!'.format(c))

                else:
                    string += c

            return string

        # Array
        if self._peek() == '[':
            if to_python:
                array = Array(self, False)
                return array.to_python()
            else:
                return Array(self, read_all)

        # Object
        if self._peek() == '{':
            if to_python:
                obj = Object(self, False)
                return obj.to_python()
            else:
                return Object(self, read_all)

        raise Exception(u'Unexpected bytes!')

    def _skip_whitespace(self):
        while True:
            self._ensure_readbuf_left(1)
            if len(self.readbuf) - self.readbuf_read < 1:
                break

            if self.readbuf[self.readbuf_read] not in FileReader._WHITESPACE:
                break

            self.readbuf_read += 1

    def _get(self):
        self._ensure_readbuf_left(1)
        if len(self.readbuf) - self.readbuf_read < 1:
            raise Exception(u'Unexpected end of file when getting next byte!')
        result = self.readbuf[self.readbuf_read]
        self.readbuf_read += 1
        return result

    def _read(self, amount):
        self._ensure_readbuf_left(amount)
        if len(self.readbuf) - self.readbuf_read < amount:
            raise Exception(u'Unexpected end of file reading a chunk!')
        result = self.readbuf[self.readbuf_read:self.readbuf_read+amount]
        self.readbuf_read += amount
        return result

    def _peek(self):
        self._ensure_readbuf_left(1)
        if len(self.readbuf) - self.readbuf_read < 1:
            return None
        return self.readbuf[self.readbuf_read]

    def _is_next(self, s):
        s_len = len(s)
        self._ensure_readbuf_left(s_len)
        if len(self.readbuf) - self.readbuf_read < s_len:
            return False
        for i in range(s_len):
            if self.readbuf[self.readbuf_read + i] != s[i]:
                return False
        return True

    def _skip_if_next(self, s):
        """ If next bytes are same as in 's', then skip them and return True.
        """
        if self._is_next(s):
            self.readbuf_read += len(s)
            return True
        return False

    def _ensure_readbuf_left(self, minimum_left):
        if len(self.readbuf) - self.readbuf_read >= minimum_left:
            return
        read_amount = max(minimum_left, FileReader._READBUF_CHUNK_SIZE) - (len(self.readbuf) - self.readbuf_read)
        self.readbuf_pos += self.readbuf_read
        self.readbuf = self.readbuf[self.readbuf_read:] + self.file.read(read_amount)
        self.readbuf_read = 0

    def _tell_read_pos(self):
        return self.readbuf_pos + self.readbuf_read

    def _seek(self, pos):
        # If position is at the area of
        # readbuffer, then just rewind it.
        if pos >= self.readbuf_pos and pos <= self.readbuf_pos + len(self.readbuf):
            self.readbuf_read = pos - self.readbuf_pos
        # If position is outside the readbuffer,
        # then read buffer from scratch
        else:
            self.readbuf = ''
            self.readbuf_read = 0
            self.readbuf_pos = pos
            self.file.seek(pos)
