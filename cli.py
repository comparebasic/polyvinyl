import argparse, json, os, time
from polyvinyl import lin, SEEK_END
from polyvinyl.utils import identifier, config, colors

def ParseCli():
    parser = argparse.ArgumentParser(
        prog="PolyVinylCli",
        description="PolyVinyl Command Line Tool")
    parser.add_argument("--in")
    parser.add_argument("--out")
    parser.add_argument("--log-color", action="store_true")
    return parser.parse_args()


def parse_arg(ar):
    try:
        ar.index("=")
        ident = identifier.Ident(ar)
        s = ident.name
    except ValueError:
        ident = None
        s = ar

    file_name, base, ext = config.get_name_ext(s)
    return (ident, file_name, base, ext)

def show(args, records):
    if args.log_color:
        print("\x1b[{}m{} records\x1b[0m".format(colors.CYAN, len(records)))
    else:
        print("{} records".format(len(records)))

    for rec in records:
        for k,v in rec.items():
            if k.find("date") != -1:
                v = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int.from_bytes(v, "big"))/1000000.0))
                
            if args.log_color:
                print("\x1b[{};{}m{}\x1b[0m: {}".format(colors.BOLD, colors.YELLOW,k,v))
            else:
                print("{}: {}".format(k,v))
        print("")
    

if __name__ == "__main__":
    args = ParseCli()

    in_ident, in_file, _, in_ext = parse_arg(getattr(args, "in"))

    if in_ident:
        print("Handle Ident")

    else:
        if in_ext == "linr":
            records = []

            with open(in_file, "rb") as f:
                f.seek(0, SEEK_END)
                while True:
                    rec = lin.map_r(f, None)
                    if not rec:
                        break

                    records.append(rec)

            show(args, records)
