from .. import BSTREAM_MAX, SEEK_END, SEEK_CUR, SEEK_START
from socket import socket as socktype

def quote(s):
    b = bytearray()
    for c in bytes(s, "utf-8"):
        if c >= ord('a') and c <= ord('z') or c >= ord('A') and c <= ord('Z'):
            b.append(c)
        else:
            b.append(ord('#'))
            b += bytearray(c.to_bytes(1, "big").hex(), 'ascii')
    return bytes(b)


def unquote(bs):
    print("Unquote {}".format(bs))
    b = bytearray()
    a = bytearray() 

    count = 0
    
    if isinstance(bs, (str)):
        bs = bytes(bs, "utf-8")

    for c in bs:
        if c == ord('#'):
            count = 2
            a = bytearray()
            continue

        if count == 2:
            a.append(c)
            count = 1
        elif count == 1:
            a.append(c)
            b += bytes.fromhex(a.decode('ascii'))
            count = 0
        else:
            b.append(c)
            
    return b.decode("utf-8")


def send(stream, arr):
    s = bytearray() 
    for seg in arr:
        if isinstance(seg, str):
            seg = bytes(seg, "utf-8")
        s += len(seg).to_bytes(2, "big")
        if isinstance(seg, str):
            s += seg.encode("utf-8")
        else:
            s += seg
    print("sending sock {}".format(s))
    if hasattr(stream, 'sendall'):
        stream.sendall(s)
    else:
        stream.write(s)


def send_r(stream, arr):
    s = bytearray() 
    for seg in arr:
        if isinstance(seg, str):
            seg = bytes(seg, "utf-8")
        s += seg
        print(s)
        s += len(seg).to_bytes(2, "big")
        print(s)
    print("sending file {}".format(s))

    if hasattr(stream, 'send'):
        stream.send(s)
    else:
        stream.write(s)


def read_next(stream):
    if hasattr(stream, 'recv'):
        length_s = stream.recv(2)
    else:
        length_s = stream.read(2)

    length = int.from_bytes(length_s, "big")
    if length == 0:
        return None
    elif length > BSTREAM_MAX:
        raise ValueError("Length exeeds max", length)

    if hasattr(stream, 'recv'):
        b = stream.recv(length)
    else:
        b = stream.read(length)

    if len(b) != length:
        raise TypeError(
            "Byte length {} does not match expected length {}".format(
                len(b), length 
            )
        )

    return b


def read_next_r(stream):
    if stream.tell() == 0:
        raise DingerNotOk("Early beginning of file reached")
    stream.seek(-2, SEEK_CUR)
    length_s = stream.read(2)
    stream.seek(-2, SEEK_CUR)

    length = int.from_bytes(length_s, "big")
    if length == 0:
        return None
    elif length > BSTREAM_MAX:
        raise ValueError("Length exeeds max", length)

    if stream.tell() == 0:
        raise DingerNotOk("Early beginning of file reached")
    stream.seek(-length, SEEK_CUR)
    b = stream.read(length)
    stream.seek(-length, SEEK_CUR)

    if len(b) != length:
        raise TypeError(
            "Byte length {} does not match expected length {}".format(
                len(b), length 
            )
        )

    return b

def latest_r(stream, key):
    value = None
    while stream.tell() > 0:
        item  = read_next_r(stream)
        if item == key:
            return value

        value = item

def map_r(stream, keys):
    key = None
    value = None
    data = {}
    while stream.tell() > 0:
        item  = read_next_r(stream)
        if value:
            key = item.decode("utf-8")
            if keys.get(key) is not None and data.get(key) is None: 
                data[key] = value 
            value = None
        else:
            value = item
    return data
    

def arr_to_dict(arr):
    data = {}
    for i in range(0, len(arr), 2):
        data[arr[i].decode("utf-8")] = arr[i+1]

    if len(arr) % 2:
        data[arr[-1]] = True

    return data
