"""Proof that nothing was lost: rebuild the dashboard's original data from src/data/ and compare
it, value by value, with the raw dump. Also prints a count report and the translation backlog.

Run:  python3 tools/dashboard/check_data.py <dashboard-raw.json> <data_dir>
"""
import json, sys, os
from build_data import untr, TIER_NAMES

raw = json.load(open(sys.argv[1], encoding="utf-8"))
D = sys.argv[2]
f = {n[:-5]: json.load(open(os.path.join(D, n), encoding="utf-8")) for n in os.listdir(D) if n.endswith(".json")}
u = {k: untr(v) for k, v in f.items()}
back_tier = {v: k for k, v in TIER_NAMES.items()}

rebuilt = {
    "DO": u["settings"]["cityOrder"], "FX": u["settings"]["fx"], "CAT": u["settings"]["categories"],
    "STOPIMG": u["settings"]["stopImages"], "DVCOL": u["settings"]["stopIconColors"],
    "BKLBL": u["settings"]["bookingLabels"], "BKC5": u["settings"]["bookingColors"],
    "BKCF": u["settings"]["bookingFilters"], "HEB_D": u["settings"]["hebrewWeekdays"],
    "C": {c: {"en": v["name"], "zh": v["zh"], "x": v["map"]["x"], "y": v["map"]["y"], "ll": v["ll"], "img": v["images"],
              "dx": v["map"]["dx"], "dy": v["map"]["dy"], "a": v["map"]["anchor"]} for c, v in u["cities"].items()},
    "CCOL": {c: v["color"] for c, v in u["cities"].items()},
    "PH": {c: v["gradient"] for c, v in u["cities"].items()},
    "W": {c: [v["weather"]["temp"], v["weather"]["desc"]] for c, v in u["cities"].items()},
    "HOT": {c: v["hotelBaseCNY"] for c, v in u["cities"].items()},
    "MUST": {c: v["mustSee"] for c, v in u["cities"].items()},
    "PLAN": {c: v["highlights"] for c, v in u["cities"].items()},
    "DIST": {c: {"from": v["distances"]["from"], **({"fromNote": v["distances"]["fromNote"]} if "fromNote" in v["distances"] else {}),
                 **({"fq": v["distances"]["mapQuery"]} if "mapQuery" in v["distances"] else {}),
                 "rows": [[r["name"], r["km"], r["time"], r["mapQuery"]] + ([r["zh"]] if "zh" in r else [])
                          for r in v["distances"]["rows"]]} for c, v in u["cities"].items()},
    "P": {c: [[p["name"], p["zh"], p["cat"], p["desc"], p["time"], p["tips"], p["img"]] + ([p["mapQuery"]] if "mapQuery" in p else [])
              for p in lst] for c, lst in u["places"].items()},
    "PR": {n: {**{k2: v[k1] for k1, k2 in [("hours", "h"), ("booking", "b"), ("advice", "a"), ("source", "src"), ("checked", "d")] if v[k1] is not None},
               **({"mon": v["closedMonday"]} if "closedMonday" in v else {})} for n, v in u["practical"].items()},
    "H": {c: {"area": u["cities"][c]["hotelArea"], "tiers": {back_tier[t]: [[h["label"], h["name"], h["rating"], h["price"], h["url"], h["mapQuery"], h["ll"]]
                                                                         for h in lst] for t, lst in tiers.items()}} for c, tiers in u["hotels"].items()},
    "HVER": u["hotel-lookups"]["verifiedLocation"], "HTRIP": u["hotel-lookups"]["tripComId"],
    "HZH": u["hotel-lookups"]["chineseName"], "HALIAS": u["hotel-lookups"]["alias"], "GNOTE": u["hotel-lookups"]["locationNote"],
    "DV": u["dayplans"],
    "DAYS": {c: [[r["label"], r["summary"], r["stops"], r["mode"], r["extra"]] for r in lst] for c, lst in u["day-routes"].items()},
    "R": u["routes"], "L": u["transport"]["legs"], "M": u["transport"]["matrix"],
    "MC": u["transport"]["modes"]["color"], "MCLS": u["transport"]["modes"]["cssClass"],
    "MLBL": u["transport"]["modes"]["label"], "IC": u["transport"]["modes"]["icon"],
    "IMG": {k: v["file"] for k, v in u["images"].items()},
    "CREDIT": {**{k: v["credit"] for k, v in u["images"].items() if "credit" in v}, **u["images-extra-credits"]},
    "_HOL": u["holidays"],
}
if "community-internal" in u and "RNP" in raw:
    rebuilt.update({"RNP": u["community-internal"]["byCity"], "RNPLV": u["community-internal"]["levels"],
                    "RNLV": u["community-internal"]["yangshuoLevels"], "RN": {"ys": u["community-internal"]["yangshuo"]}})
rebuilt["CITYX.INSET"] = u["settings"]["mapInsets"]; raw["CITYX.INSET"] = raw["CITYX"]["INSET"]
rebuilt["CITYX.ALLQ"] = u["settings"]["allPlacesQuery"]; raw["CITYX.ALLQ"] = raw["CITYX"]["ALLQ"]
rebuilt["CITYX.ANCH"] = {c: v["mainStreet"] for c, v in u["cities"].items()}; raw["CITYX.ANCH"] = raw["CITYX"]["ANCH"]
rebuilt["H.area"] = None  # area checked inside H

ok = True
for k, v in rebuilt.items():
    if v is None:
        continue
    same = json.dumps(v, sort_keys=True, ensure_ascii=False) == json.dumps(raw[k], sort_keys=True, ensure_ascii=False)
    ok &= same
    if not same:
        print("MISMATCH:", k)
print("ROUND-TRIP:", "OK — every value matches the dashboard" if ok else "PROBLEMS FOUND")

# --- Count report ---
P = u["places"]; DV = u["dayplans"]; H = u["hotels"]
print("cities", len(u["cities"]))
print("places", sum(len(v) for v in P.values()), {c: len(v) for c, v in P.items()})
print("plan days", sum(len(v["days"]) for v in DV.values()), "stops", sum(len(d["stops"]) for v in DV.values() for d in v["days"]))
print("hotels", sum(len(l) for t in H.values() for l in t.values()))
print("routes", len(u["routes"]), "legs", len(u["transport"]["legs"]), "matrix pairs", len(u["transport"]["matrix"]))
print("practical", len(u["practical"]), "images", len(u["images"]), "credits", len(rebuilt["CREDIT"]))
if "community-internal" in u:
    print("community posts", sum(len(v["items"]) for v in u["community-internal"]["byCity"].values()) + len(u["community-internal"]["yangshuo"]["items"]))
print("holidays", len(u["holidays"]))


def count(v):
    if isinstance(v, dict) and set(v.keys()) == {"he", "en"}:
        return 1, (1 if v["en"] is None else 0)
    if isinstance(v, (list, dict)):
        a = b = 0
        for x in (v.values() if isinstance(v, dict) else v):
            x1, x2 = count(x); a += x1; b += x2
        return a, b
    return 0, 0


total = todo = 0
for name in sorted(f):
    a, b = count(f[name]); total += a; todo += b
    if a:
        print(f"  translate {name}: {b} of {a} Hebrew texts need English")
print("translation backlog:", todo, "of", total)
