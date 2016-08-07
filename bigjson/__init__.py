from filereader import FileReader


def load(file):
    reader = FileReader(file)
    return reader.read()
