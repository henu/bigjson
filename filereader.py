from array import Array
from obj import Object


class FileReader:

    _WHITESPACE = '\t\n '
    _READBUF_CHUNK_SIZE = 1024*1024

    def __init__(self, file):
        self.file = file

        # This buffer is for reading and peeking
        self.readbuf = ''

    def read(self, read_all=False):
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
                if num[-1] not in '0123456790':
                    raise Exception('Expected digit after dot!')
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
            return Array(self, read_all)

        # Object
        if self._peek() == '{':
            return Object(self, read_all)

        raise Exception('Unexpected bytes!')

    def _skip_whitespace(self):
        while True:
            # Read whitespace from current readbuffer
            whitespace_in_readbuf = 0
            while whitespace_in_readbuf < len(self.readbuf) and self.readbuf[whitespace_in_readbuf] in FileReader._WHITESPACE:
                whitespace_in_readbuf += 1
            self.readbuf = self.readbuf[whitespace_in_readbuf:]

            # If readbuffer is not empty, then read more
            if len(self.readbuf) > 0:
                return

            # Readbuffer is empty, so load more
            self._fill_readbuf(FileReader._READBUF_CHUNK_SIZE)

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
