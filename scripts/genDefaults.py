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

resetIds = {"SpessaSynth": 203, "GS": 203, "GM1": 200, "GM2": 202, "XG": 205}
sendsByMode = {"GM1": [], "GM2": [91, 93], "SpessaSynth": [91, 93, 94], "GS": [91, 93, 94], "XG": [91, 93, 94]}
gsFamily = ("GS", "SpessaSynth")
vibratoIds = [76, 77, 78]
toneIds = [74, 71, 73, 75, 72]
setupSpacing = 21
channelSpacing = 41

gm1Global = [(170, 16383)]
universalGlobal = gm1Global + [(171, 8192), (172, 0), (173, 0)]
gsGlobal = [(301, 127), (300, 0), (302, 0), (303, 64)]
xgGlobal = [(500, 0), (501, 127), (502, 0), (503, 0)]

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

systemSections = {
    "GM1": [("Global", gm1Global)],
    "GM2": [
        ("Global", universalGlobal),
        ("Reverb (Hall 2)", [(210, 4), (211, 64)]),
        ("Chorus (Chorus 3)", [(212, 2), (213, 3), (214, 19), (215, 8), (216, 0)]),
    ],
    "SpessaSynth": [("Global", universalGlobal)] + gsBody,
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

systemMemos = {
    "GM1": "Bank select is ignored in GM1 mode.",
    "GM2": "Default melodic bank MSB becomes 121 and drum bank MSB 120.",
    "SpessaSynth": "Default. GS mode with 14 bit master and channel volume, pan and expression, which SpessaSynth reads in any mode.",
    "GS": "Strict Roland GS. Master settings use GS sysex only, nothing 14 bit.",
    "XG": "Bank MSB 127 selects drums.",
}


def sectionEvents(mode):
    events = []
    for title, pairs in systemSections[mode]:
        events.append(divider(title))
        for pair in pairs:
            if len(pair) > 2:
                events.append(cc(pair[0], Gate=pair[2], Value=pair[1]))
            else:
                events.append(cc(pair[0], Value=pair[1]))
    return events


def systemTemplate(ident, mode):
    events = [
        {"tag": "Memo", "text": systemMemos[mode]},
        divider("Reset"),
        cc(resetIds[mode]),
    ] + sectionEvents(mode)
    return {
        "id": ident,
        "name": "%s System Setup" % mode,
        "events": events,
    }


def channelEvents(mode):
    sends = [cc(ident, Value=0) for ident in sendsByMode[mode]]
    if mode == "SpessaSynth":
        # 14 bit channel volume, pan and expression, which SpessaSynth stores at full resolution
        head = [cc(121, Value=0), cc(160, Value=12800), cc(161, Value=0), autoPc()]
        expression = [cc(162, Value=16383)]
    else:
        head = [cc(121, Value=0), cc(7, Value=100), cc(10, Value=0), autoPc()]
        expression = [cc(11, Value=127)]
    bendAndMod = [cc(112, Value=0), cc(130, Value=2), cc(1, Value=0)]
    if mode in gsFamily:
        head = head + [cc(352, Value=1)]
    if mode == "GM1":
        return head + bendAndMod + expression
    efxAssign = [cc(374, Value=0)] if mode in gsFamily else []
    vibrato = [cc(ident, Value=64) for ident in vibratoIds]
    tone = [cc(ident, Value=64) for ident in toneIds]
    if mode != "XG":
        gsPortamento = [cc(5, Value=0), cc(65, Value=0)] if mode in gsFamily else []
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


def channelTemplate(ident, mode):
    return {
        "id": ident,
        "name": "%s Channel Init" % mode,
        "events": channelEvents(mode),
    }


def folderOf(name, items):
    return {"type": "folder", "name": name, "items": items}


def buildTemplates():
    return [
        folderOf("SpessaSynth (default)", [systemTemplate(12, "SpessaSynth"), channelTemplate(0, "SpessaSynth")]),
        folderOf("GS", [systemTemplate(10, "GS"), channelTemplate(13, "GS")]),
        folderOf("GM1", [systemTemplate(2, "GM1"), channelTemplate(11, "GM1")]),
        folderOf("GM2", [systemTemplate(3, "GM2"), channelTemplate(4, "GM2")]),
        folderOf("XG", [systemTemplate(6, "XG"), channelTemplate(7, "XG")]),
    ]


def channelTrack(channel, initTick):
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
        for index, event in enumerate(channelEvents("SpessaSynth"))
    ]
    track["events"] = [
        {
            "tag": "Comment",
            "attrs": {"Tick": 0, "Step": 0, "Text": "---- CH Setup %s" % ("-" * 48)},
        },
    ] + channelSetup + [divider("End of CH Setup")]
    return track


def buildTracks():
    system = {
        "name": "System Setup",
        "ch": 1,
        "events": [
            {
                "tag": "Comment",
                "attrs": {"Tick": 0, "Step": 0, "Text": "---- Reset %s" % ("-" * 52)},
            },
            cc(203, Step=1),
        ]
        + sectionEvents("SpessaSynth")
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
    return [system] + [channelTrack(channel, systemEndTick + 1) for channel in range(1, 17)] + [drums]


def writeDefaults():
    writeYaml(
        "defaults.yaml",
        {
            "tempo": 120,
            "timeSignature": "4/4",
            "keySignature": "C Maj",
            "endTick": 1920,
            "conductorMarks": [{"tick": 0, "name": "Setup"}, {"tick": 1920, "name": "Start"}],
            "templates": buildTemplates(),
            "tracks": buildTracks(),
        },
    )


if __name__ == "__main__":
    writeDefaults()
