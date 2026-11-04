from lib.ctl import ccm, folder, sysexSpec, val

signed64 = dict(minimum=-64, maximum=63, offset=64)
partGate = lambda: val(1, 1, 64, offset=-1, name="Part No.")
drumKey = lambda: val(36, 0, 127, name="Drum Note", kind="Key")

tableIds = {
    "monoPoly": 12,
    "offOn": 16,
    "assign": 20,
    "partMode": 21,
    "connection": 22,
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
            xgCcm(
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
                memo="Part is the track channel, parts 1 to 16. MW LFO PMOD Depth and BEND Pitch Control map to channel parameters. Other depths use dynamic modulators.",
                sync="LastEachGate",
            ),
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
                        "Normalized to 120. The gain is (data/120) squared.",
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
                        "Handled with variation in system connection.",
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


def buildXg():
    take = idCounter(500)
    return {
        "tables": buildTables(),
        "items": [
            folder(
                "Yamaha XG",
                [
                    system(take),
                    folder(
                        "XG Effects",
                        [
                            {"include": "@module/generated/effectParts/xg/%s.yaml" % name}
                            for name in ("reverb", "chorus", "variation", "insertion")
                        ],
                    ),
                    partSetup(take),
                    drumSetups(take),
                ],
            )
        ],
    }
