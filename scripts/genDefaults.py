import os

import yaml

from lib.ctl import writeYaml

partsDir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "modules",
    "spessasynth",
    "generated",
    "effectParts",
)


def partCcms(subPath):
    with open(os.path.join(partsDir, subPath), encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    found = {}

    def walk(items):
        for item in items:
            kind = item.get("type")
            if kind == "folder":
                walk(item.get("items", []))
            elif kind == "ccm":
                found[item["name"]] = item["id"]

    walk(document if isinstance(document, list) else document.get("items", []))
    return found


def loadEffects():
    return {
        "xg/reverb": partCcms(os.path.join("xg", "reverb.yaml")),
        "xg/chorus": partCcms(os.path.join("xg", "chorus.yaml")),
        "xg/variation": partCcms(os.path.join("xg", "variation.yaml")),
        "xg/insertion": partCcms(os.path.join("xg", "insertion.yaml")),
        "gs/efx": partCcms(os.path.join("gs", "efx.yaml")),
    }


divider = lambda text: {
    "tag": "Comment",
    "attrs": {"Step": 0, "Text": "---- %s %s" % (text, "-" * max(4, 60 - len(text)))},
}
cc = lambda ident, **attrs: {"tag": "CC", "attrs": dict({"ID": ident}, **attrs)}
autoPc = lambda: {"tag": "PC", "attrs": {"PC": 1, "Mode": "Auto"}}

# Variants. SS is SpessaSynth and is the GS hybrid: a GS setup plus the SpessaSynth only 14 bit
# channel controls, so there is no separate SSGS. The other hybrids (SSGM1, SSGM2, SSXG) are a
# GM1, GM2 or XG setup plus the same controls. SpessaSynth reads CC 7, 10, 11 and
# their LSBs (CC 39, 42, 43) in every system mode, so a mode switch never silences them.
variantOrder = ["SS", "GM1", "GM2", "GS", "XG", "SSGM1", "SSGM2", "SSXG"]
baseOf = {
    "SS": "GS",
    "GM1": "GM1",
    "GM2": "GM2",
    "GS": "GS",
    "XG": "XG",
    "SSGM1": "GM1",
    "SSGM2": "GM2",
    "SSXG": "XG",
}
labelOf = dict((name, name) for name in variantOrder)
labelOf["SS"] = "SpessaSynth"
isSs = lambda variant: variant.startswith("SS")
isGsFamily = lambda variant: baseOf[variant] == "GS"
defaultVariant = "SS"

resetIds = {"GS": 203, "GM1": 200, "GM2": 202, "XG": 205}
sendsByBase = {"GM1": [], "GM2": [91, 93], "GS": [91, 93, 94], "XG": [91, 93, 94]}
vibratoIds = [76, 77, 78]
toneIds = [74, 71, 73, 75, 72]
setupSpacing = 21
channelSpacing = 41

gm1Global = [(170, 16383)]
universalGlobal = gm1Global + [(171, 8192), (172, 0), (173, 0)]
gsGlobal = [(301, 127), (300, 0), (302, 0), (303, 64)]
xgGlobal = [(500, 0), (501, 127), (502, 0), (503, 0)]
# 7 bit master volumes. A hybrid sends the 14 bit universal master volume (170) instead.
sevenBitMasterVolumes = (301, 501)

effects = loadEffects()


def fx(kind, name):
    return effects[kind][name]


gsBody = [
    (
        "Reverb (Hall 2)",
        [(310, 4), (311, 4), (312, 0), (313, 64), (314, 64), (315, 0), (316, 0)],
    ),
    (
        "Chorus (Chorus 3)",
        [
            (320, 2),
            (321, 0),
            (322, 64),
            (323, 8),
            (324, 80),
            (325, 3),
            (326, 19),
            (327, 0),
            (328, 0),
        ],
    ),
    (
        "EFX (Thru)",
        [
            (fx("gs/efx", "EFX Type"), 0),
            (fx("gs/efx", "Send Level to Reverb"), 40),
            (fx("gs/efx", "Send Level to Chorus"), 0),
            (fx("gs/efx", "Send Level to Delay"), 0),
        ],
    ),
    (
        "Delay (Delay 1)",
        [
            (330, 0),
            (331, 0),
            (332, 97),
            (333, 1),
            (334, 1),
            (335, 127),
            (336, 0),
            (337, 0),
            (338, 64),
            (339, 80),
            (340, 0),
        ],
    ),
]


plainSections = {
    "GM1": [("Global", gm1Global)],
    "GM2": [
        ("Global", universalGlobal),
        ("Reverb (Hall 2)", [(210, 4), (211, 64)]),
        ("Chorus (Chorus 3)", [(212, 2), (213, 3), (214, 19), (215, 8), (216, 0)]),
    ],
    "GS": [("Global", gsGlobal)] + gsBody,
    "XG": [
        ("Global", xgGlobal),
        ("Reverb (Hall 1)", [
            (fx("xg/reverb", "XG Reverb Type"), 128),
            (fx("xg/reverb", "Reverb Return"), 64),
            (fx("xg/reverb", "Reverb Pan"), 64),
        ]),
        ("Chorus (Chorus 1)", [
            (fx("xg/chorus", "XG Chorus Type"), 8320),
            (fx("xg/chorus", "Chorus Return"), 64),
            (fx("xg/chorus", "Chorus Pan"), 64),
            (fx("xg/chorus", "Chorus Send To Reverb"), 0),
        ]),
        ("Variation (Thru)", [
            (fx("xg/variation", "XG Variation Type"), 8192),
            (fx("xg/variation", "Variation Return"), 64),
            (fx("xg/variation", "Variation Pan"), 64),
            (fx("xg/variation", "Variation Send To Reverb"), 0),
            (fx("xg/variation", "Variation Send To Chorus"), 0),
            (fx("xg/variation", "Variation Connection"), 0),
            (fx("xg/variation", "Variation Part Number"), 128),
        ]),
    ]
    + [
        (
            "Insertion %d (Off)" % number,
            [
                (fx("xg/insertion", "XG Insertion Effects Type"), 8192, number),
                (fx("xg/insertion", "Insertion Part Number"), 128, number),
            ],
        )
        for number in range(1, 5)
    ],
}


def systemSections(variant):
    base = baseOf[variant]
    sections = plainSections[base]
    if not isSs(variant):
        return sections
    title, pairs = sections[0]
    merged = universalGlobal + [
        pair
        for pair in pairs
        if pair not in universalGlobal and pair[0] not in sevenBitMasterVolumes
    ]
    return [(title, merged)] + sections[1:]


baseMemos = {
    "GM1": "Bank select is ignored in GM1 mode.",
    "GM2": "Default melodic bank MSB becomes 121 and drum bank MSB 120.",
    "GS": "Strict Roland GS. Master settings use GS sysex only, nothing 14 bit.",
    "XG": "Bank MSB 127 selects drums.",
}
hybridNote = "SpessaSynth hybrid: %s setup plus 14 bit master and channel volume, pan and expression, which SpessaSynth reads in any mode. "


def systemMemo(variant):
    if isSs(variant):
        base = baseOf[variant]
        note = hybridNote % base
        if variant == "SS":
            return "Default. " + note + "GS master volume is replaced by the 14 bit one."
        if base == "GS":
            return note + "GS master volume is replaced by the 14 bit one."
        if base == "XG":
            return note + "XG master volume is replaced by the 14 bit one. " + baseMemos[base]
        return note + baseMemos[base]
    return baseMemos[variant]


def sectionEvents(variant):
    events = []
    for title, pairs in systemSections(variant):
        events.append(divider(title))
        for pair in pairs:
            if len(pair) > 2:
                events.append(cc(pair[0], Gate=pair[2], Value=pair[1]))
            else:
                events.append(cc(pair[0], Value=pair[1]))
    return events


def systemTemplate(ident, variant):
    events = [
        {"tag": "Memo", "text": systemMemo(variant)},
        divider("Reset"),
        cc(resetIds[baseOf[variant]]),
    ] + sectionEvents(variant)
    return {
        "id": ident,
        "name": "%s System Setup" % labelOf[variant],
        "events": events,
    }


def channelEvents(variant):
    base = baseOf[variant]
    sends = [cc(ident, Value=0) for ident in sendsByBase[base]]
    if isSs(variant):
        # 14 bit channel volume, pan and expression, which SpessaSynth stores at full resolution
        head = [cc(121, Value=0), cc(160, Value=12800), cc(161, Value=0), autoPc()]
        expression = [cc(162, Value=16383)]
    else:
        head = [cc(121, Value=0), cc(7, Value=100), cc(10, Value=0), autoPc()]
        expression = [cc(11, Value=127)]
    bendAndMod = [cc(112, Value=0), cc(130, Value=2), cc(1, Value=0)]
    if base == "GS":
        head = head + [cc(352, Value=1)]
    if base == "GM1":
        return head + bendAndMod + expression
    efxAssign = [cc(374, Value=0)] if base == "GS" else []
    vibrato = [cc(ident, Value=64) for ident in vibratoIds]
    tone = [cc(ident, Value=64) for ident in toneIds]
    if base != "XG":
        gsPortamento = [cc(5, Value=0), cc(65, Value=0)] if base == "GS" else []
        return head + sends + bendAndMod + expression + vibrato + tone + efxAssign + gsPortamento
    extras = [
        cc(5, Value=0),
        cc(65, Value=0),
        cc(64, Value=0),
        cc(67, Value=0),
        cc(134, Value=64),
        cc(131, Value=0),
        cc(133, Value=0),
    ]
    return head + [cc(508, Gate=1, Value=1)] + sends + bendAndMod + expression + vibrato + tone + extras


def channelTemplate(ident, variant):
    return {
        "id": ident,
        "name": "%s Channel Init" % labelOf[variant],
        "events": channelEvents(variant),
    }


def folderOf(name, items):
    return {"type": "folder", "name": name, "items": items}


# Template ids per variant: (system setup, channel init). Existing ids are kept stable.
templateIds = {
    "SS": (12, 0),
    "GS": (10, 13),
    "GM1": (2, 11),
    "GM2": (3, 4),
    "XG": (6, 7),
    "SSGM1": (14, 15),
    "SSGM2": (16, 17),
    "SSXG": (20, 21),
}
folderNames = {
    "SS": "SpessaSynth (default)",
    "SSGM1": "SSGM1 (SpessaSynth + GM1)",
    "SSGM2": "SSGM2 (SpessaSynth + GM2)",
    "SSXG": "SSXG (SpessaSynth + XG)",
}


def buildTemplates():
    # Every variant keeps its templates in all builds, only the starter project differs.
    return [
        folderOf(
            folderNames.get(variant, variant),
            [
                systemTemplate(templateIds[variant][0], variant),
                channelTemplate(templateIds[variant][1], variant),
            ],
        )
        for variant in variantOrder
    ]


def channelTrack(channel, initTick, variant):
    track = {"name": "CH%02d" % channel, "ch": channel}
    if channel == 10:
        track["mode"] = "Rhythm"
    if channel == 1:
        track["current"] = True
    channelSetup = [
        dict(
            event,
            attrs=dict(
                event.get("attrs", {}),
                Tick=initTick + index * channelSpacing,
            ),
        )
        for index, event in enumerate(channelEvents(variant))
    ]
    track["events"] = [
        {
            "tag": "Comment",
            "attrs": {"Tick": 0, "Step": 0, "Text": "---- CH Setup %s" % ("-" * 48)},
        },
    ] + channelSetup + [divider("End of CH Setup")]
    return track


def buildTracks(variant):
    system = {
        "name": "System Setup",
        "ch": 1,
        "events": [
            {
                "tag": "Comment",
                "attrs": {"Tick": 0, "Step": 0, "Text": "---- Reset %s" % ("-" * 52)},
            },
            cc(resetIds[baseOf[variant]], Step=1),
        ]
        + sectionEvents(variant)
        + [divider("End of System Setup")],
    }
    system["events"] = [
        event if event.get("tag") == "Comment" and event.get("attrs", {}).get("Text", "").startswith("---- Reset")
        else dict(event, attrs=dict(event.get("attrs", {}), Step=setupSpacing))
        for event in system["events"]
    ]
    system["events"][1]["attrs"]["Step"] = 1
    systemEndTick = sum(event.get("attrs", {}).get("Step", 0) for event in system["events"])
    drums = {
        "name": "Drum Key-Based Controllers",
        "ch": 10,
        "mode": "Rhythm",
        "events": [
            {
                "tag": "Comment",
                "attrs": {
                    "Tick": 0,
                    "Step": 0,
                    "Text": "---- Drum Parameter %s" % ("-" * 44),
                },
            },
            {"tag": "PC", "attrs": {"PC": 1, "Mode": "Drumset", "Step": 1}},
            cc(152, Gate=36, Value=120, Step=3),
            divider("End of Drum Parameter"),
        ],
    }
    return [system] + [channelTrack(channel, systemEndTick + 1, variant) for channel in range(1, 17)] + [drums]


def writeDefaults(variant=defaultVariant):
    if variant not in baseOf:
        raise SystemExit("Unknown default data variant: %s (use %s)" % (variant, ", ".join(variantOrder)))
    writeYaml(
        "defaults.yaml",
        {
            "tempo": 120,
            "timeSignature": "4/4",
            "keySignature": "C Maj",
            "endTick": 1920,
            "conductorMarks": [{"tick": 0, "name": "Setup"}, {"tick": 1920, "name": "Start"}],
            "templates": buildTemplates(),
            "tracks": buildTracks(variant),
        },
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Write build/defaults.yaml for one default data variant.")
    parser.add_argument("--variant", default=defaultVariant, type=str.upper, choices=variantOrder)
    writeDefaults(parser.parse_args().variant)
