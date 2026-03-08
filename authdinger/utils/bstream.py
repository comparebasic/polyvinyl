def add(s, seg):
    length = length(seg)
    if length < 256:
        s += '\0' 
    s += length.to_bytes()
    s += seg
    return s
