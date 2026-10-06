from lib.ctl import ccm, experimental, folder, sysexSpec, val

signed64 = dict(minimum=-64, maximum=63, offset=64)
partGate = lambda: val(1, 1, 64, offset=-1, name="Part No.")
drumKey = lambda: val(36, 0, 127, name="Drum Note", kind="Key")
word = lambda msb, lsb: msb * 128 + lsb
partOrOff = lambda: val(128, 1, 128, offset=-1, name="Part No.", tableId=27)

tableIds = {
    "monoPoly": 12,
    "offOn": 16,
    "assign": 20,
    "partMode": 21,
    "connection": 22,
    "reverb": 23,
    "chorus": 24,
    "variation": 25,
    "xgController": 26,
    "partOff": 27,
}

assignModes = [(0, "Single"), (1, "Multi"), (2, "Inst (drum)")]
partModes = [
    (0, "Normal"),
    (1, "Drum"),
    (2, "Drum Setup 1"),
    (3, "Drum Setup 2"),
    (4, "Drum Setup 3"),
    (5, "Drum Setup 4"),
]
connections = [(0, "Insertion"), (1, "System")]
reverbTypes = [
    (word(0x00, 0x00), "NO EFFECT"),
    (word(0x01, 0x00), "HALL 1"),
    (word(0x01, 0x01), "HALL 2"),
    (word(0x02, 0x00), "ROOM 1"),
    (word(0x02, 0x01), "ROOM 2"),
    (word(0x02, 0x02), "ROOM 3"),
    (word(0x03, 0x00), "STAGE 1"),
    (word(0x03, 0x01), "STAGE 2"),
    (word(0x04, 0x00), "PLATE"),
    (word(0x10, 0x00), "WHITE ROOM"),
    (word(0x11, 0x00), "TUNNEL"),
    (word(0x12, 0x00), "CANYON"),
    (word(0x13, 0x00), "BASEMENT"),
]
chorusTypes = [
    (word(0x00, 0x00), "NO EFFECT"),
    (word(0x41, 0x00), "CHORUS 1"),
    (word(0x41, 0x01), "CHORUS 2"),
    (word(0x41, 0x02), "CHORUS 3"),
    (word(0x41, 0x08), "CHORUS 4"),
    (word(0x42, 0x00), "CELESTE 1"),
    (word(0x42, 0x01), "CELESTE 2"),
    (word(0x42, 0x02), "CELESTE 3"),
    (word(0x42, 0x08), "CELESTE 4"),
    (word(0x43, 0x00), "FLANGER 1"),
    (word(0x43, 0x01), "FLANGER 2"),
    (word(0x43, 0x08), "FLANGER 3"),
    (word(0x08, 0x00), "SYMPHONIC"),
]
variationTypes = [(word(0x00, 0x00), "NO EFFECT"), (word(0x40, 0x00), "THRU")]
insertionTypes = variationTypes

depthGroups = [
    ("MW", 0x1D),
    ("BEND", 0x23),
    ("CAT", 0x4D),
    ("PAT", 0x53),
    ("AC1", 0x5A),
    ("AC2", 0x61),
]
depthNames = [
    "Pitch Control",
    "Filter Control",
    "Amplitude Control",
    "LFO PMOD Depth",
    "LFO FMOD Depth",
    "LFO AMOD Depth",
]


def toEntries(pairs):
    return dict((number, label) for number, label in pairs)


def buildTables():
    depth = {}
    for name, start in depthGroups:
        for index, label in enumerate(depthNames):
            depth[start + index] = "%s %s" % (name, label)
    return [
        {"id": tableIds["assign"], "entries": toEntries(assignModes)},
        {"id": tableIds["partMode"], "entries": toEntries(partModes)},
        {"id": tableIds["connection"], "entries": toEntries(connections)},
        {"id": tableIds["reverb"], "entries": toEntries(reverbTypes)},
        {"id": tableIds["chorus"], "entries": toEntries(chorusTypes)},
        {"id": tableIds["variation"], "entries": toEntries(variationTypes)},
        {"id": tableIds["xgController"], "entries": depth},
        {"id": tableIds["partOff"], "entries": {128: "OFF"}},
    ]


def idCounter(start):
    state = {"next": start}

    def take():
        state["next"] += 1
        return state["next"] - 1

    return take


def xgCcm(ident, name, address, payload, value, gate=None, memo=None, sync="Last"):
    return ccm(
        ident,
        name,
        value=value,
        gate=gate,
        memo=memo,
        sync=sync,
        sysex=sysexSpec("xg", address, payload),
    )


def system(take):
    return folder(
        "XG System",
        [
            xgCcm(
                take(),
                "Master Tune",
                "00H 00H 00H",
                "#VF4 #VF3 #VF2 #VF1",
                val(0, -1000, 1000, 1024, name="0.1 cent"),
                memo="Four nibbles, most significant first. Wire value is 1024 plus the tuning.",
            ),
            xgCcm(take(), "Master Volume", "00H 00H 04H", "#VL", val(127)),
            xgCcm(
                take(),
                "Master Attenuator",
                "00H 00H 05H",
                "#VL",
                val(0),
                memo="Inverted master volume. 0 is no attenuation.",
            ),
            xgCcm(
                take(),
                "Master Transpose",
                "00H 00H 06H",
                "#VL",
                val(0, name="Semitones", **signed64),
            ),
        ],
    )


def partSetup(take):
    part = lambda name, byte, value, memo=None: xgCcm(
        take(), name, "08H #GL %02XH" % byte, "#VL", value, gate=partGate(), memo=memo
    )
    alias = lambda cc: "Alias of CC%d." % cc
    return folder(
        "XG Part Setup",
        [
            part("Bank Select MSB", 0x01, val(0), alias(0)),
            part("Bank Select LSB", 0x02, val(0), alias(32)),
            part(
                "Program Change",
                0x03,
                val(1, 1, 128, offset=-1, name="Program"),
                "Same as a Program Change on that part. Send the bank first.",
            ),
            part(
                "Receive Channel",
                0x04,
                val(0),
                "0 is channel 1. Parts above the synth channel count are discarded.",
            ),
            part("Mono/Poly", 0x05, val(1, 0, 1, tableId=tableIds["monoPoly"])),
            part(
                "Same Note Number Key On Assign",
                0x06,
                val(2, 0, 2, tableId=tableIds["assign"]),
            ),
            part(
                "Part Mode",
                0x07,
                val(0, 0, 5, tableId=tableIds["partMode"]),
                "Non-zero turns the part into a drum channel. Switching to drums resets the program to 0.",
            ),
            part("Note Shift", 0x08, val(0, name="Semitones", **signed64)),
            part("Volume", 0x0B, val(100), alias(7)),
            part("Velocity Sense Depth", 0x0C, val(64)),
            part("Velocity Sense Offset", 0x0D, val(64)),
            part(
                "Pan",
                0x0E,
                val(64),
                "0 is random pan for every new voice. " + alias(10),
            ),
            part("Chorus Send", 0x12, val(0), alias(93)),
            part("Reverb Send", 0x13, val(0), alias(91)),
            part("Vibrato Rate", 0x15, val(64), alias(76)),
            part("Vibrato Depth", 0x16, val(64), alias(77)),
            part("Vibrato Delay", 0x17, val(64), alias(78)),
            part("Filter Cutoff", 0x18, val(64), alias(74)),
            part("Filter Resonance", 0x19, val(64), alias(71)),
            part("EG Attack Time", 0x1A, val(64), alias(73)),
            part("EG Decay Time", 0x1B, val(64), alias(75)),
            part("EG Release Time", 0x1C, val(64), alias(72)),
            part(
                "Bend Pitch Control",
                0x23,
                val(2, name="Semitones", **signed64),
                "Sets the pitch wheel range.",
            ),
        ],
    )


def partSetupExperimental(take):
    part = lambda name, byte, value, memo: xgCcm(
        take(),
        name,
        "08H #GL %02XH" % byte,
        "#VL",
        value,
        gate=partGate(),
        memo=experimental(memo),
    )
    controllerDepth = xgCcm(
        take(),
        "Controller Depth (track channel part)",
        "08H #CH #GL",
        "#VL",
        val(64),
        gate=val(
            0x1D,
            0x1D,
            0x66,
            name="Source and Parameter",
            tableId=tableIds["xgController"],
        ),
        memo=experimental(
            "Part is the track channel, parts 1 to 16. MW LFO PMOD Depth and BEND Pitch Control map to channel parameters. Other depths use dynamic modulators."
        ),
        sync="LastEachGate",
    )
    return folder(
        "XG Part Setup (Experimental 4.4.0)",
        [
            part(
                "Dry Level",
                0x11,
                val(127),
                "Dry level of the part when routed through effects.",
            ),
            part(
                "AC1 Controller Number",
                0x59,
                val(16),
                "Assignable controller 1 number.",
            ),
            part(
                "AC2 Controller Number",
                0x60,
                val(17),
                "Assignable controller 2 number.",
            ),
            part(
                "Portamento Switch",
                0x67,
                val(0, 0, 1, tableId=tableIds["offOn"]),
                "Alias of CC65. ON becomes 127.",
            ),
            part("Portamento Time", 0x68, val(0), "Alias of CC5."),
            controllerDepth,
        ],
    )


def drumSetups(take):
    setups = []
    for setup in range(4):
        row = lambda name, byte, value, memo=None: xgCcm(
            take(),
            "%s (Drum %d)" % (name, setup + 1),
            "%02XH #GL %02XH" % (0x30 + setup, byte),
            "#VL",
            value,
            gate=drumKey(),
            memo=memo,
            sync="LastEachGate",
        )
        setups.append(
            folder(
                "XG Drum Setup %d" % (setup + 1),
                [
                    row(
                        "Pitch Coarse",
                        0x00,
                        val(0, name="Semitones", **signed64),
                        "100 cent steps.",
                    ),
                    row("Pitch Fine", 0x01, val(0, name="Cents", **signed64)),
                    row(
                        "Level",
                        0x02,
                        val(120),
                        "Normalized to 120. Gain is (data/120) squared in 4.4.0 and data/120 in stable builds.",
                    ),
                    row(
                        "Alternate Group",
                        0x03,
                        val(0),
                        "Overrides the exclusive class.",
                    ),
                    row(
                        "Pan",
                        0x04,
                        val(64),
                        "0 is random. In 4.4.0 a value of 64 leaves the channel pan unchanged.",
                    ),
                    row("Reverb Send", 0x05, val(127)),
                    row("Chorus Send", 0x06, val(127)),
                    row(
                        "Variation Send",
                        0x07,
                        val(127),
                        experimental(
                            "Handled only by 4.4.0 and only with variation in system connection."
                        ),
                    ),
                    row(
                        "Rcv Note Off",
                        0x09,
                        val(0, 0, 1, tableId=tableIds["offOn"]),
                        "On ends the drum note at Note Off.",
                    ),
                    row("Rcv Note On", 0x0A, val(1, 0, 1, tableId=tableIds["offOn"])),
                ],
            )
        )
    return folder(
        "XG Drum Setup (applies to every drum channel using the setup)", setups
    )


def effectNote(text=None):
    base = "Types other than NO EFFECT and THRU have no DSP in SpessaSynth 4.4.0. Unknown reverb and chorus types are silent, unknown variation and insertion types pass dry."
    return experimental(base if text is None else text + " " + base)


def paramRow(take, address, name, wide=False, default=64):
    payload = "#VH #VL" if wide else "#VL"
    value = val(default, 0, 16383 if wide else 127)
    return xgCcm(
        take(), name, address, payload, value, memo=effectNote("Stored but unused.")
    )


def typeRow(take, name, address, tableId, default):
    return xgCcm(
        take(),
        "%s Type" % name,
        address,
        "#VH #VL",
        val(default, 0, 16383, tableId=tableId),
        memo=effectNote(),
    )


def lowParams(take, first, count, start, label):
    return [
        paramRow(
            take, "02H 01H %02XH" % (start + i), "%s Parameter %d" % (label, first + i)
        )
        for i in range(count)
    ]


def reverbBlock(take):
    items = [
        typeRow(take, "Reverb", "02H 01H 00H", tableIds["reverb"], word(0x01, 0x00))
    ]
    items += lowParams(take, 1, 10, 0x02, "Reverb")
    items += [
        xgCcm(
            take(),
            "Reverb Return",
            "02H 01H 0CH",
            "#VL",
            val(64),
            memo=effectNote("Return level is applied."),
        ),
        xgCcm(
            take(),
            "Reverb Pan",
            "02H 01H 0DH",
            "#VL",
            val(64),
            memo=effectNote("Pan is applied."),
        ),
    ]
    items += lowParams(take, 11, 6, 0x10, "Reverb")
    return folder("XG Reverb (Experimental 4.4.0)", items)


def chorusBlock(take):
    items = [
        typeRow(take, "Chorus", "02H 01H 20H", tableIds["chorus"], word(0x41, 0x00))
    ]
    items += lowParams(take, 1, 10, 0x22, "Chorus")
    items += [
        xgCcm(
            take(), "Chorus Return", "02H 01H 2CH", "#VL", val(64), memo=effectNote()
        ),
        xgCcm(take(), "Chorus Pan", "02H 01H 2DH", "#VL", val(64), memo=effectNote()),
        xgCcm(
            take(),
            "Chorus Send To Reverb",
            "02H 01H 2EH",
            "#VL",
            val(0),
            memo=effectNote(),
        ),
    ]
    items += lowParams(take, 11, 6, 0x30, "Chorus")
    return folder("XG Chorus (Experimental 4.4.0)", items)


def variationBlock(take):
    items = [
        typeRow(
            take, "Variation", "02H 01H 40H", tableIds["variation"], word(0x40, 0x00)
        )
    ]
    items += [
        paramRow(
            take,
            "02H 01H %02XH" % (0x42 + 2 * i),
            "Variation Parameter %d (14-bit)" % (i + 1),
            True,
        )
        for i in range(10)
    ]
    items += [
        xgCcm(
            take(), "Variation Return", "02H 01H 56H", "#VL", val(64), memo=effectNote()
        ),
        xgCcm(
            take(), "Variation Pan", "02H 01H 57H", "#VL", val(64), memo=effectNote()
        ),
        xgCcm(
            take(),
            "Variation Send To Reverb",
            "02H 01H 58H",
            "#VL",
            val(0),
            memo=effectNote(),
        ),
        xgCcm(
            take(),
            "Variation Send To Chorus",
            "02H 01H 59H",
            "#VL",
            val(0),
            memo=effectNote(),
        ),
        xgCcm(
            take(),
            "Variation Connection",
            "02H 01H 5AH",
            "#VL",
            val(0, 0, 1, tableId=tableIds["connection"]),
            memo=effectNote(
                "Insertion routes one part through the effect. System makes it a send effect."
            ),
        ),
        xgCcm(
            take(),
            "Variation Part Number",
            "02H 01H 5BH",
            "#VL",
            partOrOff(),
            memo=effectNote("Used in insertion connection. 128 is Off (wire 127)."),
        ),
    ]
    items += lowParams(take, 11, 6, 0x70, "Variation")
    return folder("XG Variation (Experimental 4.4.0)", items)


def insertionBlock(take, number):
    base = lambda byte: "03H %02XH %02XH" % (number - 1, byte)
    label = "Insertion %d" % number
    items = [
        xgCcm(
            take(),
            "%s Type" % label,
            base(0x00),
            "#VH #VL",
            val(word(0x40, 0x00), 0, 16383, tableId=tableIds["variation"]),
            memo=effectNote(),
        )
    ]
    items += [
        paramRow(take, base(0x02 + i), "%s Parameter %d" % (label, i + 1))
        for i in range(10)
    ]
    items += [
        xgCcm(
            take(),
            "%s Part Number" % label,
            base(0x0C),
            "#VL",
            partOrOff(),
            memo=effectNote("128 is Off (wire 127)."),
        )
    ]
    items += [
        paramRow(take, base(0x20 + i), "%s Parameter %d" % (label, 11 + i))
        for i in range(6)
    ]
    items += [
        paramRow(
            take, base(0x30 + 2 * i), "%s Parameter %d (14-bit)" % (label, i + 1), True
        )
        for i in range(10)
    ]
    return folder("XG Insertion %d (Experimental 4.4.0)" % number, items)


def effects(take):
    return folder(
        "XG Effects (Experimental 4.4.0)",
        [
            reverbBlock(take),
            chorusBlock(take),
            variationBlock(take),
            folder(
                "XG Insertion Effects", [insertionBlock(take, n) for n in range(1, 5)]
            ),
        ],
    )


def buildXg():
    take = idCounter(500)
    return {
        "tables": buildTables(),
        "items": [
            folder(
                "Yamaha XG",
                [
                    system(take),
                    partSetup(take),
                    partSetupExperimental(take),
                    drumSetups(take),
                    effects(take),
                ],
            )
        ],
    }
