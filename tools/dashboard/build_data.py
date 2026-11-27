"""Turn the raw dashboard dump (dashboard-raw.json) into organised content files in src/data/.

Every text that contains Hebrew becomes {"he": "...", "en": null}: "en": null marks text
still waiting for an English translation. Names that are already English/Chinese stay plain.

Run:  python3 tools/dashboard/build_data.py <dashboard-raw.json> <out_dir>
"""
import json, re, sys, os

HEB = re.compile(r'[֐-׿]')


def tr(v):
    """Wrap every Hebrew string (recursively) as a translatable text."""
    if isinstance(v, str):
        return {"he": v, "en": None} if HEB.search(v) else v
    if isinstance(v, list):
        return [tr(x) for x in v]
    if isinstance(v, dict):
        return {k: tr(x) for k, x in v.items()}
    return v


TIER_NAMES = {"0.75": "budget", "1": "recommended", "1.8": "luxury"}


def build(raw):
    d = raw
    out = {}

    # --- Cities --------------------------------------------------------------
    cities = {}
    for cid in d["DO"]:
        c = d["C"][cid]
        cities[cid] = {
            "name": c["en"], "zh": c["zh"], "ll": c["ll"], "images": c["img"],
            "map": {"x": c["x"], "y": c["y"], "dx": c["dx"], "dy": c["dy"], "anchor": c["a"]},
            "color": d["CCOL"][cid], "gradient": d["PH"][cid],
            "weather": {"temp": d["W"][cid][0], "desc": tr(d["W"][cid][1])},
            "hotelArea": tr(d["H"][cid]["area"]),
            "hotelBaseCNY": d["HOT"][cid],
            "mainStreet": d["CITYX"]["ANCH"][cid],
            "mustSee": d["MUST"][cid],
            "highlights": d["PLAN"][cid],
            "distances": {
                "from": d["DIST"][cid]["from"],
                **({"fromNote": tr(d["DIST"][cid]["fromNote"])} if "fromNote" in d["DIST"][cid] else {}),
                **({"mapQuery": d["DIST"][cid]["fq"]} if "fq" in d["DIST"][cid] else {}),
                "rows": [{"name": r[0], "km": r[1], "time": tr(r[2]), "mapQuery": r[3],
                          **({"zh": r[4]} if len(r) > 4 else {})} for r in d["DIST"][cid]["rows"]],
            },
        }
    out["cities"] = cities

    # --- Places (the cards in "יעדים") ---------------------------------------
    places = {}
    for cid in d["DO"]:
        places[cid] = [{
            "name": p[0], "zh": p[1], "cat": p[2], "desc": tr(p[3]), "time": tr(p[4]),
            "tips": tr(p[5]), "img": p[6], **({"mapQuery": p[7]} if len(p) > 7 else {}),
        } for p in d["P"][cid]]
    out["places"] = places

    # --- Practical info (hours, tickets) — only verified sources -------------
    out["practical"] = {name: {
        "hours": tr(v.get("h")), "booking": tr(v.get("b")), "advice": tr(v.get("a")),
        "source": v.get("src"), "checked": v.get("d"), **({"closedMonday": v["mon"]} if "mon" in v else {}),
    } for name, v in d["PR"].items()}

    # --- Hotels ---------------------------------------------------------------
    hotels = {}
    for cid in d["DO"]:
        hotels[cid] = {TIER_NAMES[t]: [{
            "label": tr(h[0]), "name": h[1], "rating": tr(h[2]), "price": tr(h[3]),
            "url": h[4], "mapQuery": h[5], "ll": h[6],
        } for h in lst] for t, lst in d["H"][cid]["tiers"].items()}
    out["hotels"] = hotels
    out["hotel-lookups"] = {
        "verifiedLocation": d["HVER"], "tripComId": d["HTRIP"], "chineseName": d["HZH"],
        "alias": d["HALIAS"], "locationNote": tr(d["GNOTE"]),
    }

    # --- Day plans --------------------------------------------------------------
    out["dayplans"] = {cid: tr(d["DV"][cid]) for cid in d["DO"]}
    out["day-routes"] = {cid: [{
        "label": tr(r[0]), "summary": r[1], "stops": r[2], "mode": r[3], "extra": tr(r[4]),
    } for r in d["DAYS"][cid]] for cid in d["DO"]}

    # --- Routes and transport ---------------------------------------------------
    out["routes"] = tr(d["R"])
    out["transport"] = {
        "legs": tr(d["L"]), "matrix": tr(d["M"]),
        "modes": {"color": d["MC"], "cssClass": d["MCLS"], "label": tr(d["MLBL"]), "icon": d["IC"]},
    }

    # --- Images and credits -----------------------------------------------------
    out["images"] = {k: {"file": v, **({"credit": d["CREDIT"][k]} if k in d["CREDIT"] else {})}
                     for k, v in d["IMG"].items()}
    out["images-extra-credits"] = {k: v for k, v in d["CREDIT"].items() if k not in d["IMG"]}

    # --- Community tips (RedNote) — INTERNAL: summarise before showing publicly ---
    # Not stored in the public repository: the source is the RedNote research docs in the Claude project.
    if "RNP" in d:
        out["community-internal"] = tr({"byCity": d["RNP"], "levels": d["RNPLV"],
                                        "yangshuo": d["RN"]["ys"], "yangshuoLevels": d["RNLV"]})

    # --- Calendar, money, labels --------------------------------------------------
    out["holidays"] = tr(d["_HOL"])
    out["settings"] = {
        "cityOrder": d["DO"], "fx": d["FX"], "categories": tr(d["CAT"]),
        "stopImages": d["STOPIMG"], "stopIconColors": d["DVCOL"],
        "mapInsets": tr(d["CITYX"]["INSET"]), "allPlacesQuery": d["CITYX"]["ALLQ"],
        "bookingLabels": tr(d["BKLBL"]), "bookingColors": d["BKC5"], "bookingFilters": tr(d["BKCF"]),
        "hebrewWeekdays": d["HEB_D"],
    }
    return out


def untr(v):
    if isinstance(v, dict) and set(v.keys()) == {"he", "en"}:
        return v["he"]
    if isinstance(v, list):
        return [untr(x) for x in v]
    if isinstance(v, dict):
        return {k: untr(x) for k, x in v.items()}
    return v


if __name__ == "__main__":
    raw = json.load(open(sys.argv[1], encoding="utf-8"))
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    for name, data in build(raw).items():
        with open(os.path.join(out_dir, name + ".json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print("wrote", len(build(raw)), "files to", out_dir)
