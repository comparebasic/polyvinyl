from .. import BSTREAM_MAX
from socket import socket as socktype

START = 0
CUR = 1
END = 2

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
    b = bytearray()
    a = bytearray() 

    count = 0
    
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
            s += seg.encode("utf-8")
        else:
            s += seg
        if isinstance(seg, str):
            seg = bytes(seg, "utf-8")
        s += len(seg).to_bytes(2, "big")
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

    return b.decode("utf-8")


def read_next_r(stream):
    stream.seek(-2, CUR)
    length_s = stream.read(2)
    length = int.from_bytes(length_s, "big")
    if length == 0:
        return None
    elif length > BSTREAM_MAX:
        raise ValueError("Length exeeds max", length)

    stream.seek(-length, CUR)
    b = stream.read(length)

    if len(b) != length:
        raise TypeError(
            "Byte length {} does not match expected length {}".format(
                len(b), length 
            )
        )

    return b.decode("utf-8")


def arr_to_dict(arr):
    data = {}
    for i in range(0, len(arr), 2):
        data[arr[i]] = arr[i+1]

    if len(arr) % 2:
        data[arr[-1]] = True

    return data
