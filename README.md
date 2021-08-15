bigjson
=======

Python library that reads JSON files of any size.

The magic is in the Array and Object types.
They load stuff from the file only when necessary.

The library expects files to be opened in binary mode.


Example
-------

The file size in this example is 78 GB.

```
import bigjson

with open('wikidata-latest-all.json', 'rb') as f:
    j = bigjson.load(f)
    element = j[4]
    print(element['type'])
    print(element['id'])
```


Testing
=======

```
pytest-3 .
```
