from lib.ctl import writeYaml

divider = lambda text: {
    "tag": "Comment",
    "attrs": {"Step": 0, "Text": "---- %s %s" % (text, "-" * max(4, 60 - len(text)))},
}
cc = lambda ident, **attrs: {"tag": "CC", "attrs": dict({"ID": ident}, **attrs)}
autoPc = lambda: {"tag": "PC", "attrs": {"PC": 1, "Mode": "Auto"}}

resetIds = {"GS": 203, "GM1": 200, "GM2": 202, "XG": 205}
sendsByMode = {"GM1": [], "GM2": [91, 93], "GS": [91, 93, 94], "XG": [91, 93, 94]}
vibratoIds = [76, 77, 78]
toneIds = [74, 71, 73, 75, 72]

universalGlobal = [(170, 16383), (171, 8192), (172, 0), (173, 0)]
gsGlobal = [(301, 127), (300, 0), (302, 0), (303, 64)]
xgGlobal = [(500, 0), (501, 127), (502, 0), (503, 0)]

systemSections = {
    "GM1": [("Global", universalGlobal)],
    "GM2": [
        ("Global", universalGlobal),
        ("Reverb (Hall 2)", [(210, 4), (211, 64)]),
        ("Chorus (Chorus 3)", [(212, 2), (213, 3), (214, 19), (215, 8), (216, 0)]),
    ],
    "GS": [
        ("Global", universalGlobal + gsGlobal),
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
        ("EFX Insertion (Thru)", [(345, 0), (347, 40), (348, 0), (349, 0)]),
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
    ],
    "XG": [
        ("Global", universalGlobal + xgGlobal),
        ("Reverb (Hall 1, Experimental)", [(573, 128), (584, 64), (585, 64)]),
        (
            "Chorus (Chorus 1, Experimental)",
            [(592, 8320), (603, 64), (604, 64), (605, 0)],
        ),
        (
            "Variation (Thru, Experimental)",
            [
                (612, 8192),
                (623, 64),
                (624, 64),
                (625, 0),
                (626, 0),
                (627, 0),
                (628, 128),
            ],
        ),
    ]
    + [
        (
            "Insertion %d (Off, Experimental)" % (index + 1),
            [(typeId, 8192), (partId, 128)],
        )
        for index, (typeId, partId) in enumerate(
            [(635, 646), (663, 674), (691, 702), (719, 730)]
        )
    ],
}

systemMemos = {
    "GM1": "Bank select is ignored in GM1 mode.",
    "GM2": "Default melodic bank MSB becomes 121 and drum bank MSB 120.",
    "GS": "Default mode. Native SpessaSynth system.",
    "XG": "Bank MSB 127 selects drums. XG effects need the SpessaSynth 4.4.0 experimental branch.",
}


def sectionEvents(mode):
    return [
        event
        for title, pairs in systemSections[mode]
        for event in [divider(title)]
        + [cc(ident, Value=value) for ident, value in pairs]
    ]


def systemTemplate(ident, mode, spaced=False):
    events = [
        {"tag": "Memo", "text": systemMemos[mode]},
        divider("Reset"),
        cc(resetIds[mode]),
    ] + sectionEvents(mode)
    if spaced:
        # Space system-wide setup messages too, so hardware receives reset and
        # global/effect settings before any channel initialization.
        events = [
            event if event.get("tag") == "Memo" else dict(
                event, attrs=dict(event.get("attrs", {}), Step=4)
            )
            for event in events
        ]
    return {
        "id": ident,
        "name": "%s System Setup (%s)" % (mode, "Spaced" if spaced else "Immediate"),
        "events": events,
    }


def channelEvents(mode):
    sends = [cc(ident, Value=0) for ident in sendsByMode[mode]]
    head = [cc(121, Value=0), cc(7, Value=100), cc(10, Value=0), autoPc()]
    expression = [cc(11, Value=127)]
    bendAndMod = [cc(112, Value=0), cc(1, Value=0)]
    if mode == "GS":
        head = head + [cc(352, Value=1)]
    if mode == "GM1":
        return head + bendAndMod + expression
    efxAssign = [cc(374, Value=0)] if mode == "GS" else []
    vibrato = [cc(ident, Value=64) for ident in vibratoIds]
    tone = [cc(ident, Value=64) for ident in toneIds]
    if mode != "XG":
        return head + sends + bendAndMod + expression + vibrato + tone + efxAssign
    extras = [
        cc(5, Value=0),
        cc(65, Value=0),
        cc(64, Value=0),
        cc(67, Value=0),
        cc(130, Value=2),
        cc(134, Value=64),
        cc(131, Value=0),
        cc(133, Value=0),
    ]
    return head + [cc(127)] + sends + bendAndMod + expression + vibrato + tone + extras


def channelTemplate(ident, mode, spaced=False):
    events = channelEvents(mode)
    if spaced:
        # Step is a delta from the previous event
        events = [dict(event, attrs=dict(event.get("attrs", {}), Step=4)) for event in events]
    return {
        "id": ident,
        "name": "%s Channel Init (%s)" % (mode, "Spaced" if spaced else "Immediate"),
        "events": events,
    }


def folderOf(name, items):
    return {"type": "folder", "name": name, "items": items}


def buildTemplates():
    return [
        folderOf("GS (default)", [systemTemplate(10, "GS"), systemTemplate(30, "GS", True), channelTemplate(0, "GS"), channelTemplate(20, "GS", True)]),
        folderOf("GM1", [systemTemplate(2, "GM1"), systemTemplate(31, "GM1", True), channelTemplate(11, "GM1"), channelTemplate(21, "GM1", True)]),
        folderOf("GM2", [systemTemplate(3, "GM2"), systemTemplate(32, "GM2", True), channelTemplate(4, "GM2"), channelTemplate(22, "GM2", True)]),
        folderOf("XG", [systemTemplate(6, "XG"), systemTemplate(33, "XG", True), channelTemplate(7, "XG"), channelTemplate(23, "XG", True)]),
    ]


def channelTrack(channel):
    track = {"name": "CH%02d" % channel, "ch": channel}
    if channel == 10:
        track["mode"] = "Rhythm"
    if channel == 1:
        track["current"] = True
    track["events"] = [
        {
            "tag": "Comment",
            "attrs": {"Tick": 0, "Step": 0, "Text": "---- CH Setup %s" % ("-" * 48)},
        },
        {"tag": "Template", "attrs": {"ID": 0, "Step": 1}},
        divider("End of CH Setup"),
    ]
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
        + sectionEvents("GS")
        + [divider("End of System Setup")],
    }
    system["events"] = [
        event if event.get("tag") == "Comment" and event.get("attrs", {}).get("Text", "").startswith("---- Reset")
        else dict(event, attrs=dict(event.get("attrs", {}), Step=4))
        for event in system["events"]
    ]
    system["events"][1]["attrs"]["Step"] = 1
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
    return [system] + [channelTrack(channel) for channel in range(1, 17)] + [drums]


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
