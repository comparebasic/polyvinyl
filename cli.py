import argparse, json, os, time, datetime, math
from polyvinyl import lin, SEEK_END
from polyvinyl.utils import identifier, config, colors, token as token_d, tbl

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
                v = token_d.time_from_bytes(v)
                
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
        if in_ext == "fmt":
            with open(in_file, "r") as f:

                
                
                headers, items = tbl.parse(f)
                print(headers)

                start_date = None
                total = 0.0

                for rec in items:
                    for i, x in enumerate(rec):
                        rec[i] = x.strip()
                        
                    cost = float(rec[2])
                    total += cost
                    rec.append(total)

                max_width = [0, 0, 0, 0]
                for rec in items:
                    for i, x in enumerate(rec):
                        l = len(str(x))
                        if l > max_width[i]:
                            max_width[i] = l


                for rec in items:
                    cost = float(rec[2])
                    if rec[1]:
                        parts = rec[1].split("-")

                        dt = datetime.datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                        if not start_date:
                            start_date = dt
                            print("  Start {}".format(start_date))
                        else:
                            d = (dt - start_date).days
                            if math.floor(d / 7) > 0:
                                while math.floor(d / 7):
                                    start_date = start_date + datetime.timedelta(days=7)
                                    print("  Week starting {}".format(start_date))
                                    d -=  7



                    if cost > 0:
                        color = 32
                    else:
                        color = 33

                    if total > 0:
                        tcolor = 0 
                    else:
                        tcolor = 31

                    pads = [
                        (max_width[0] - len(rec[0]) + 2) * ' ',
                        (max_width[1] - len(rec[1]) + 2) * ' ',
                        (max_width[2] - len(str(rec[2])) + 2) * ' ',
                        (max_width[3] - len(str(rec[3])) + 2) * ' '
                    ]

                    print("\x1b[1;{}m{}{}\x1b[22m{}{}{}{}\x1b[{}m{}{}".format(
                        color,
                        rec[0],
                        pads[0],
                        rec[1],
                        pads[1],
                        pads[2],
                        cost,
                        tcolor,
                        pads[3],
                        rec[3]
                    ))

                

        if in_ext == "linr":
            records = []

            with open(in_file, "rb") as f:
                f.seek(0, SEEK_END)
                while True:
                    rec = lin.next_rec(f, None)
                    if not rec:
                        break

                    records.append(rec)

            show(args, records)
