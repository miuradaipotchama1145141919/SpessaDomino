import os
import yaml

outDir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "build",
)

experimentalTag = "Experimental 4.4.0"


class noAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def writeYaml(name, data):
    os.makedirs(outDir, exist_ok=True)
    with open(os.path.join(outDir, name), "w", encoding="utf-8") as handle:
        yaml.dump(
            data,
            handle,
            Dumper=noAliasDumper,
            sort_keys=False,
            width=220,
            allow_unicode=True,
        )


def drop(spec):
    return dict((key, val) for key, val in spec.items() if val is not None)


def val(
    default=None,
    minimum=None,
    maximum=127,
    offset=None,
    name=None,
    kind=None,
    tableId=None,
    entries=None,
):
    return drop(
        {
            "default": default,
            "min": minimum,
            "max": maximum,
            "offset": offset,
            "name": name,
            "type": kind,
            "tableId": tableId,
            "entries": (
                [{"label": label, "value": number} for number, label in entries]
                if entries
                else None
            ),
        }
    )


def ccm(
    ident,
    name,
    data=None,
    value=None,
    gate=None,
    memo=None,
    sync=None,
    sysex=None,
    color=None,
):
    return drop(
        {
            "type": "ccm",
            "id": ident,
            "name": name,
            "color": color,
            "sync": sync,
            "value": value,
            "gate": gate,
            "memo": memo,
            "data": data,
            "sysex": sysex,
        }
    )


def folder(name, items, ident=None):
    return drop({"type": "folder", "id": ident, "name": name, "items": items})


def experimental(text):
    return "[%s] %s" % (experimentalTag, text)


def sysexSpec(profile, address, payload=""):
    return {"profile": profile, "address": address, "payload": payload}


colorByType = {
    "select": "0050D0",
    "mix": "008000",
    "send": "00A0A0",
    "pitch": "C000C0",
    "sound": "8040D0",
    "perform": "808000",
    "config": "707070",
    "drum": "C06000",
    "awe": "904020",
    "master": "900000",
    "reset": "E00000",
    "reverb": "0080E0",
    "chorus": "00B060",
    "delay": "D0A000",
    "variation": "D05090",
    "insert": "B00060",
}

folderRules = [
    ("system reset", "reset"),
    ("channel mode", "perform"),
    ("awe32", "awe"),
    ("sf2", "config"),
    ("drum", "drum"),
    ("reverb", "reverb"),
    ("chorus", "chorus"),
    ("delay", "delay"),
    ("variation", "variation"),
    ("insertion", "insert"),
    ("efx", "insert"),
    ("master", "master"),
    ("universal", "master"),
    ("xg system", "master"),
]

nameRules = [
    ("^gm2 reverb", "reverb"),
    ("^gm2 chorus", "chorus"),
    ("efx", "insert"),
    ("send", "send"),
    ("bank|tone number|program change", "select"),
    ("volume|pan|balance|expression|level", "mix"),
    ("pitch|bend|tuning|modulation|pressure|key shift|note shift", "pitch"),
    ("vibrato|cutoff|resonance|attack|decay|release|brightness|tvf|eg ", "sound"),
    ("portamento|pedal|mono|poly|omni|notes off|sound off|reset all", "perform"),
]


def colorType(name, folderName):
    import re

    folderMatch = [kind for key, kind in folderRules if key in folderName.lower()]
    nameMatch = [
        kind for pattern, kind in nameRules if re.search(pattern, name.lower())
    ]
    return (folderMatch + nameMatch + ["config"])[0]


def colorize(doc):
    def walk(items, folderName):
        return [
            (
                dict(item, items=walk(item["items"], item["name"]))
                if item.get("type") == "folder"
                else (
                    item
                    if item.get("color") or item.get("type") != "ccm"
                    else dict(
                        item, color=colorByType[colorType(item["name"], folderName)]
                    )
                )
            )
            for item in items
        ]

    return dict(doc, items=walk(doc["items"], ""))
