# `Lin` format

The `Lin` format is essentially as follows: two bytes are used to communicate
the length of the following bytes. Then after the content the next two bytes
indicate another set of bytes. This is expected to be read until a zero length
is encountered.

```
\{0}\{5}Ident\{0}\{32}register=test%40cb%2elocal@email\{0}\{0}
```

can be though of as:

```
    5: Ident
    32: register=test%40cb%2elocal@email
    0:
```

Where "Ident" is 5 bytes long and "register=test%40cb%2elocal@email" is 32 bytes long.

## `Lin` streaming vs file storage

`Lin` has two variants, one for streaming and one for persistance. The
difference is that `Lin` on disk puts length values after the content so that
it can be read and updated at the end of the file. In other-words `Lin` files
are access by reading the end of the file first.

For socket and network conversations it makes sense to start with the length,
and then send the content. For file storage the opposite has more value. This
is because files can be added to, and the last value is always the latest one.
For this reason the file based `Lin` storage looks as follows.

The `Lin` file storage is the opposite:

```
\{0}\{0}Ident\{0}\{5}register=test%40cb%2elocal@email\{0}\{32}
```

can be though of as:

```
     0, Ident, 5, register=test%40cb%2elocal@email, 32
```


