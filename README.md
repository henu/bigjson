bigjson
=======

Python library that reads JSON files of any size.

The magic is in the Array and Object types. They load stuff from
the file only when necessary and then forget it to save memory.

TODO
----

- Make reading faster. One idea is to use some kind of lookup table in Object.

- Do not read strings as Python strings, as those need to be readed fully into memory.

- Add as many equivalent functions to Array and Object that are in list and in dict in Python.

Usage example
-------------

The file size here is 78 GB.

```
import bigjson

with open('wikidata-latest-all.json', 'rb') as f:
    j = bigjson.load(f)
    element = j[4]
    print element['type']
    print element['id']
```

Although the program is really slow, it finally parses the beginning of the JSON file and prints two strings from it.
