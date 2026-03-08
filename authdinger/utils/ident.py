class Ident(object):
    def __init__(self, ident):
        parts = ident.split("@")
        self.ident = ident
        self.tag = None
        self.ext = None
        self.idx = None
        self.source = None
        self.base = None
        if len(parts) == 1:
            self.tag = ident
            self.source = None
            self.idx = None
        else:
            self.tag = parts[0]
            try:
                self.idx = int(parts[1]) 
            except ValueError:
                self.source = parts[1]
                eparts = self.source.split('.')
                if len(eparts) > 1 :
                    self.ext = eparts[-1]
                    self.base = "".join(eparts[:-1])
                else:
                    self.base = self.source

    def __str__(self):
        return "Ident<{}@{}/{}/{} {}>".format(
            self.tag, self.base, self.source, self.idx, self.ext) 
