
def parse(stream):
    headers = [] 
    items = []
    
    for line in stream.readlines():
        line = line.strip()
        if line.startswith("+"):
            headers = [x.strip() for x in line[1:].split(",")]
        else:
            it = [x.strip() for x in line.split(",")]
            if len(it) != len(headers):
                raise TypeError("Column count mismatch", headers, it)
            items.append(it)

    return headers, items
