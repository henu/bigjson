from .filereader import FileReader


def load(file, encoding='utf-8'):
    reader = FileReader(file, encoding)
    return reader.read()
