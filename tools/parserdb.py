import os
import sys
import json
import sqlite3
import argparse

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from Rommer.core.parse_meta import RDB

parser = argparse.ArgumentParser(description="Parse RDB files to JSON or sqlite3 db.")
parser.add_argument("--base", type=str, help="Base directory of RDB files or a single RDB file.")
parser.add_argument("--type", type=str, default="json", help="Output format: json or db.")
parser.add_argument("--output", type=str, default="data", help="Output directory.")
args = parser.parse_args()

if not os.path.exists(args.output):
    os.mkdir(args.output)

if os.path.isdir(args.base):
    base = args.base
    fps = os.listdir(base)
    files = [os.path.join(args.base, fp) for fp in fps if fp.endswith(".rdb")]
else:
    files = [args.base]

res = []
for file in files:
    name = ".".join(os.path.split(file)[1].split(".")[:-1])
    rdb = RDB(file)
    print("parsing", file)
    print(f"expect {rdb.expect_num} entries, parsed {len(rdb.parsed_data)} entries.")
    if args.type == "json":
        out = os.path.join(args.output, name + ".json")
        json.dump(rdb.parsed_data, open(out, "w"), indent=4)  # noqa: SIM115
        print("dumped to", out, "\n")
    elif args.type == "db":
        df = pd.DataFrame(rdb.parsed_data)
        df["platform"] = name
        res.append(df)
    else:
        raise ValueError("Invalid output format.")

if args.type == "db":
    r = pd.concat(res)
    conn = sqlite3.connect(os.path.join(args.output, "rdb.db"))
    r.to_sql(name="meta", con=conn, index=False, if_exists="replace")
    conn.close()
    print("dumped to", os.path.join(args.output, "rdb.db"))
