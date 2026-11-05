import os
import yaml

outDir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "build",
)

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


def sysexSpec(profile, address, payload=""):
    return {"profile": profile, "address": address, "payload": payload}


# Colors follow one idea: the same function has the same color wherever it
# appears (a reverb send is teal in a part, a drum note and a drum NRPN alike),
# in dark, saturated tones that stay readable on Domino's white lists. The
# palette keeps related functions in related hues.
palette = {
    "volume": "000099",
    "pan": "CC0099",
    "expression": "660099",
    "bank": "800080",
    "modulation": "0000CC",
    "reverb": "006666",
    "chorus": "0066CC",
    "variation": "993300",
    "vibrato": "000066",
    "filter": "440000",
    "envelope": "440066",
    "portamento": "339999",
    "hold": "333333",
    "sostenuto": "9999CC",
    "soft": "666666",
    "rpn": "006600",
    "nrpn": "003399",
    "data": "996600",
    "bend": "800000",
    "channelPressure": "660000",
    "keyPressure": "440000",
    "omni": "CC0000",
    "master": "CC00FF",
    "tuning": "006600",
    "system": "000000",
    "eq": "FF3366",
    "resetGs": "0000FF",
    "resetXg": "CC0000",
    "resetGm": "000000",
    "velocity": "993366",
    "voices": "CC6699",
    "group": "003399",
    "noteRx": "000066",
    "insert": "990033",
    "controller": "6600CC",
    "plain": "000000",
}

# Folder wide rules come first: (folder fragment, name pattern or None, color)
folderRules = [
    ("system reset", r"^gs", "resetGs"),
    ("system reset", r"^xg", "resetXg"),
    ("system reset", None, "resetGm"),
    ("awe32", r"lfo to pitch|env to pitch", "modulation"),
    ("awe32", r"lfo to volume", "volume"),
    ("awe32", r"lfo to filter|env to filter|filter", "filter"),
    ("awe32", r"chorus", "chorus"),
    ("awe32", r"reverb", "reverb"),
    ("awe32", r"fine tune", "tuning"),
    ("awe32", r"lfo", "vibrato"),
    ("awe32", r"env", "envelope"),
    ("sf2", None, "data"),
    ("midi tuning", None, "tuning"),
    ("gs reverb", None, "reverb"),
    ("gs chorus", None, "chorus"),
    ("gs delay", None, "variation"),
    ("gm2 global", r"^gm2 reverb", "reverb"),
    ("gm2 global", r"^gm2 chorus", "chorus"),
]

nameRules = [
    (r"^any rpn|rpn null", "rpn"),
    (r"^any nrpn", "nrpn"),
    (r"^any control change", "plain"),
    (r"omni", "omni"),
    (r"channel pressure", "channelPressure"),
    (r"poly key pressure", "keyPressure"),
    (r"master (volume|attenuator)", "master"),
    (r"master (pan|balance)", "pan"),
    (r"master|transpose|key shift|note shift|coarse tuning|fine tuning|fine tune|tuning", "tuning"),
    (r"efx assign|^efx", "insert"),
    (r"eq switch|^eq ", "eq"),
    (r"reverb", "reverb"),
    (r"chorus", "chorus"),
    (r"variation|delay send", "variation"),
    (r"bank (select|msb|lsb)|tone number|program|source drum set", "bank"),
    (r"rx\. note|rcv note", "noteRx"),
    (r"alternate group|assign group|exclusive", "group"),
    (r"assign mode|same note", "voices"),
    (r"velocity sense", "velocity"),
    (r"balance|pan", "pan"),
    (r"expression", "expression"),
    (r"modulation", "modulation"),
    (r"volume|level", "volume"),
    (r"vibrato|lfo", "vibrato"),
    (r"cutoff|resonance|brightness|tvf|filter", "filter"),
    (r"attack|decay|release|eg |env", "envelope"),
    (r"portamento", "portamento"),
    (r"sustain pedal", "hold"),
    (r"all sound off|reset all|all notes off|^mono|^poly|mono/poly", "hold"),
    (r"sostenuto", "sostenuto"),
    (r"soft pedal", "soft"),
    (r"bend", "bend"),
    (r"pitch coarse|pitch fine|play note number", "bend"),
    (r"pitch|tuning", "tuning"),
    (r"controller (number|depth)", "controller"),
    (r"rx\. channel|receive channel|rhythm|part mode", "plain"),
]


def colorFor(name, folderName=""):
    import re

    lowerName = name.lower()
    lowerFolder = folderName.lower()
    for fragment, pattern, key in folderRules:
        if fragment in lowerFolder and (pattern is None or re.search(pattern, lowerName)):
            return palette[key]
    if "drum" in lowerFolder and re.search(r"pitch|play note", lowerName):
        return palette["bend"]
    for pattern, key in nameRules:
        if re.search(pattern, lowerName):
            return palette[key]
    return palette["plain"]


def colorize(doc):
    def walk(items, folderName):
        return [
            (
                dict(item, items=walk(item["items"], item["name"]))
                if item.get("type") == "folder"
                else (
                    item
                    if item.get("color") or item.get("type") != "ccm"
                    else dict(item, color=colorFor(item["name"], folderName))
                )
            )
            for item in items
        ]

    return dict(doc, items=walk(doc["items"], ""))


# The effect parameter blocks: the system effects keep their own color, the
# per type parameters of the variation, insertion and EFX blocks are colored
# by what they do.
blockColors = {
    "xg/reverb": "reverb",
    "xg/chorus": "chorus",
}
blockHeaders = {
    "xg/variation": "variation",
    "xg/insertion": "insert",
    "gs/efx": "insert",
}


def effectColor(name, block):
    import re

    if block in blockColors:
        return palette[blockColors[block]]
    lowerName = name.lower()
    if "eq switch" in lowerName:
        return palette["eq"]
    if re.search(r"send (level )?to reverb", lowerName):
        return palette["reverb"]
    if re.search(r"send (level )?to chorus", lowerName):
        return palette["chorus"]
    if re.search(r"send (level )?to delay", lowerName):
        return palette["variation"]
    if re.search(r"\btype\b|connection|part number|return|control (source|depth)|^send", lowerName) and not re.search(
        r"^(amp|filter|mod wave|lo-fi|wah|aw|hum|discnz|w/p|tp|radio|vowel|flg|cho|ph|od|ds|eh|enh)", lowerName
    ):
        if re.search(r"^(xg )?(variation|insertion|efx)|^(control|send)|connection|return|part number", lowerName):
            return palette[blockHeaders[block]]
    if re.search(r"\bpan\b|\bpan\(|pan dev|direction", lowerName):
        return palette["pan"]
    if re.search(r"\beq\b|eq:|hpf|lpf|low (freq|gain|level)|high (freq|gain|level)|mid\d? (freq|gain|q)|tone low|cutoff|post filter|pre filter|\bfilter\b|band\d|damp|\bq\b", lowerName):
        return palette["eq"]
    if re.search(r"level|balance|feedback|mix|gain|output|sens|threshold|sustain|\bratio\b", lowerName):
        return palette["volume"]
    return palette["plain"]


def colorizeEffects(document, block):
    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "ccm" and not node.get("color"):
                node["color"] = effectColor(node["name"], block)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(document)
    return document
