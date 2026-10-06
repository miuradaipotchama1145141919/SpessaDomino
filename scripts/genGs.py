from lib.ctl import ccm, experimental, folder, sysexSpec, val

macroReverb = [
    (0, "Room 1"),
    (1, "Room 2"),
    (2, "Room 3"),
    (3, "Hall 1"),
    (4, "Hall 2"),
    (5, "Plate"),
    (6, "Delay"),
    (7, "Panning Delay"),
]
macroChorus = [
    (0, "Chorus 1"),
    (1, "Chorus 2"),
    (2, "Chorus 3"),
    (3, "Chorus 4"),
    (4, "Feedback Chorus"),
    (5, "Flanger"),
    (6, "Short Delay"),
    (7, "Short Delay (FB)"),
]
monoPoly = [(0, "Mono"), (1, "Poly")]
assignModes = [(0, "Single"), (1, "Limited Multi"), (2, "Full Multi")]
rhythmModes = [(0, "Off (melodic)"), (1, "Drum Map 1"), (2, "Drum Map 2")]
offOn = [(0, "Off"), (1, "On")]
rxChannels = [(index, "Ch %d" % (index + 1)) for index in range(16)] + [(16, "Off")]
efxTypes = [
    (0x0000, "Thru"),
    (0x0100, "Stereo EQ"),
    (0x0120, "Phaser"),
    (0x0121, "Auto Wah"),
    (0x0125, "Tremolo"),
    (0x0126, "Auto Pan"),
    (0x1108, "PH / Auto Wah"),
]
signed64 = dict(minimum=-64, maximum=63, offset=64)
keyGate = val(36, 0, 127, name="Drum Note", kind="Key")

tableIds = {
    "reverb": 10,
    "chorus": 11,
    "monoPoly": 12,
    "assign": 13,
    "rhythm": 14,
    "rxChannel": 15,
    "offOn": 16,
    "efx": 17,
    "controller": 18,
}

controllerNames = ["MOD", "BEND", "CAT", "PAF", "CC1", "CC2"]
controllerParams = [
    "Pitch Control",
    "Filter Cutoff",
    "Amplitude",
    "LFO1 Rate",
    "LFO1 Pitch Depth",
    "LFO1 TVF Depth",
    "LFO1 TVA Depth",
    "LFO2 Rate",
    "LFO2 Pitch Depth",
    "LFO2 TVF Depth",
    "LFO2 TVA Depth",
]


def toEntries(pairs):
    return dict((number, label) for number, label in pairs)


def buildTables():
    controller = {}
    for source, sourceName in enumerate(controllerNames):
        for param, paramName in enumerate(controllerParams):
            controller[source * 16 + param] = "%s %s" % (sourceName, paramName)
    return [
        {"id": tableIds["reverb"], "entries": toEntries(macroReverb)},
        {"id": tableIds["chorus"], "entries": toEntries(macroChorus)},
        {"id": tableIds["monoPoly"], "entries": toEntries(monoPoly)},
        {"id": tableIds["assign"], "entries": toEntries(assignModes)},
        {"id": tableIds["rhythm"], "entries": toEntries(rhythmModes)},
        {"id": tableIds["rxChannel"], "entries": toEntries(rxChannels)},
        {"id": tableIds["offOn"], "entries": toEntries(offOn)},
        {"id": tableIds["efx"], "entries": toEntries(efxTypes)},
        {"id": tableIds["controller"], "entries": controller},
    ]


def gsCcm(ident, name, address, payload, value, gate=None, memo=None, sync="Last"):
    return ccm(
        ident,
        name,
        value=value,
        gate=gate,
        memo=memo,
        sync=sync,
        sysex=sysexSpec("gs", address, payload),
    )


def master():
    return folder(
        "GS Master",
        [
            gsCcm(
                300,
                "Master Tune",
                "40H 00H 00H",
                "#VF4 #VF3 #VF2 #VF1",
                val(0, -1000, 1000, 1024, name="0.1 cent"),
                memo="Four nibbles, most significant first. Wire value is 1024 plus the tuning. Assumes #VF1 is the lowest nibble.",
            ),
            gsCcm(301, "Master Volume", "40H 00H 04H", "#VL", val(127)),
            gsCcm(
                302,
                "Master Key Shift",
                "40H 00H 05H",
                "#VL",
                val(0, name="Semitones", **signed64),
                memo="Range -24 to +24 on real GS hardware.",
            ),
            gsCcm(
                303,
                "Master Pan",
                "40H 00H 06H",
                "#VL",
                val(64, 1, 127),
                memo="64 is center.",
            ),
        ],
    )


def effects():
    macro = lambda ident, name, address, table, manual, default=0: gsCcm(
        ident,
        name,
        address,
        "#VL",
        val(default, 0, 7 if table else 9, tableId=table),
        memo="Sets every parameter of the processor to a preset. See SC-8850 Owner's Manual page %d. SpessaSynth resets to Hall 2, Chorus 3 and Delay 1."
        % manual,
    )
    plain = lambda ident, name, address, default=64, memo=None, maximum=127: gsCcm(
        ident, name, address, "#VL", val(default, 0, maximum), memo=memo
    )
    return [
        folder(
            "GS Reverb",
            [
                macro(310, "Reverb Macro", "40H 01H 30H", tableIds["reverb"], 81, 4),
                gsCcm(
                    311,
                    "Reverb Character",
                    "40H 01H 31H",
                    "#VL",
                    val(4, 0, 7, tableId=tableIds["reverb"]),
                    memo="Characters 0 to 5 use the Dattorro model. 6 is a delay line, 7 a ping-pong delay.",
                ),
                plain(312, "Reverb Pre-LPF", "40H 01H 32H", 0, maximum=7),
                plain(313, "Reverb Level", "40H 01H 33H", 64),
                plain(314, "Reverb Time", "40H 01H 34H", 64),
                plain(315, "Reverb Delay Feedback", "40H 01H 35H", 0),
                plain(316, "Reverb Pre-Delay Time", "40H 01H 37H", 0),
            ],
        ),
        folder(
            "GS Chorus",
            [
                macro(320, "Chorus Macro", "40H 01H 38H", tableIds["chorus"], 83, 2),
                plain(321, "Chorus Pre-LPF", "40H 01H 39H", 0, maximum=7),
                plain(322, "Chorus Level", "40H 01H 3AH", 64),
                plain(323, "Chorus Feedback", "40H 01H 3BH", 8),
                plain(324, "Chorus Delay", "40H 01H 3CH", 80),
                plain(325, "Chorus Rate", "40H 01H 3DH", 3),
                plain(326, "Chorus Depth", "40H 01H 3EH", 19),
                plain(327, "Chorus Send Level to Reverb", "40H 01H 3FH", 0),
                plain(328, "Chorus Send Level to Delay", "40H 01H 40H", 0),
            ],
        ),
        folder(
            "GS Delay",
            [
                macro(330, "Delay Macro", "40H 01H 50H", None, 85),
                plain(331, "Delay Pre-LPF", "40H 01H 51H", 0, maximum=7),
                plain(332, "Delay Time Center", "40H 01H 52H", 97),
                plain(333, "Delay Time Ratio Left", "40H 01H 53H", 1),
                plain(334, "Delay Time Ratio Right", "40H 01H 54H", 1),
                plain(335, "Delay Level Center", "40H 01H 55H", 127),
                plain(336, "Delay Level Left", "40H 01H 56H", 0),
                plain(337, "Delay Level Right", "40H 01H 57H", 0),
                plain(338, "Delay Level", "40H 01H 58H", 64),
                plain(339, "Delay Feedback", "40H 01H 59H", 80),
                plain(340, "Delay Send Level to Reverb", "40H 01H 5AH", 0),
            ],
        ),
        folder(
            "GS Insertion Effect (EFX)",
            [
                gsCcm(
                    345,
                    "EFX Type",
                    "40H 03H 00H",
                    "#VH #VL",
                    val(0, 0, 16383, tableId=tableIds["efx"]),
                    memo="Only the types SpessaSynth implements are listed. Any other type passes the signal dry (Thru). Value is MSB*128+LSB.",
                ),
                gsCcm(
                    346,
                    "EFX Parameter",
                    "40H 03H #GL",
                    "#VL",
                    val(64),
                    gate=val(1, 1, 20, offset=2, name="Parameter No."),
                    memo="Parameters 1 to 20. Meaning depends on the EFX type. Send the type first, it resets all parameters.",
                    sync="LastEachGate",
                ),
                gsCcm(347, "EFX Send Level to Reverb", "40H 03H 17H", "#VL", val(40)),
                gsCcm(348, "EFX Send Level to Chorus", "40H 03H 18H", "#VL", val(0)),
                gsCcm(349, "EFX Send Level to Delay", "40H 03H 19H", "#VL", val(0)),
            ],
        ),
    ]


def part():
    partCcm = lambda ident, name, offsetByte, value, memo=None, gate=None: gsCcm(
        ident, name, "40H #1RCH %s" % offsetByte, "#VL", value, memo=memo, gate=gate
    )
    toneModify = [
        ("Vibrato Rate", 0x30),
        ("Vibrato Depth", 0x31),
        ("TVF Cutoff", 0x32),
        ("TVF Resonance", 0x33),
        ("EG Attack", 0x34),
        ("EG Decay", 0x35),
        ("EG Release", 0x36),
        ("Vibrato Delay", 0x37),
    ]
    modifies = [
        partCcm(366 + index, "Tone Modify: " + name, "%02XH" % byte, val(64))
        for index, (name, byte) in enumerate(toneModify)
    ]
    return folder(
        "GS Part (current track channel)",
        [
            gsCcm(
                350,
                "Tone Number (Bank MSB and Program)",
                "40H #1RCH 00H",
                "#GL #VL",
                val(1, 1, 128, offset=-1, name="Program"),
                gate=val(0, 0, 127, name="Bank MSB"),
                memo="Bank MSB and Program Change in one message.",
            ),
            partCcm(
                351, "Rx. Channel", "02H", val(0, 0, 16, tableId=tableIds["rxChannel"])
            ),
            partCcm(
                352, "Mono/Poly", "13H", val(1, 0, 1, tableId=tableIds["monoPoly"])
            ),
            partCcm(
                353, "Assign Mode", "14H", val(2, 0, 2, tableId=tableIds["assign"])
            ),
            partCcm(
                354,
                "Use for Rhythm Part",
                "15H",
                val(0, 0, 2, tableId=tableIds["rhythm"]),
                memo="Turns any channel into a drum channel. SpessaSynth has no limit on drum channels.",
            ),
            partCcm(
                355, "Pitch Key Shift", "16H", val(0, name="Semitones", **signed64)
            ),
            partCcm(356, "Part Level", "19H", val(100), memo="Alias of CC7."),
            partCcm(357, "Velocity Sense Depth", "1AH", val(64)),
            partCcm(358, "Velocity Sense Offset", "1BH", val(64)),
            partCcm(
                359,
                "Part Panpot",
                "1CH",
                val(64, 0, 127),
                memo="0 is random pan for every new voice. Alias of CC10.",
            ),
            partCcm(360, "CC1 Controller Number", "1FH", val(16)),
            partCcm(361, "CC2 Controller Number", "20H", val(17)),
            partCcm(362, "Chorus Send Level", "21H", val(0), memo="Alias of CC93."),
            partCcm(363, "Reverb Send Level", "22H", val(0), memo="Alias of CC91."),
            partCcm(
                364,
                "Pitch Fine Tune",
                "2AH",
                val(0, -8192, 8191, 8192, name="Fine"),
                memo="14 bit, range of +/-100 cents.",
            ),
            partCcm(365, "Delay Send Level", "2CH", val(0), memo="Alias of CC94."),
            gsCcm(
                374,
                "EFX Assign",
                "40H #2RCH 22H",
                "#VL",
                val(0, 0, 1, tableId=tableIds["offOn"]),
                memo="Routes this part through the EFX. Bypass is the reset state.",
            ),
        ]
        + modifies
        + [
            gsCcm(
                375,
                "Controller Depth (any source)",
                "40H #2RCH #GL",
                "#VL",
                val(64),
                gate=val(
                    0,
                    0,
                    90,
                    name="Source and Parameter",
                    tableId=tableIds["controller"],
                ),
                memo="MOD, BEND, CAT, PAF, CC1, CC2 destinations. Implemented with dynamic modulators. MOD LFO1 Pitch Depth and BEND Pitch Control map to channel parameters.",
                sync="LastEachGate",
            ),
        ],
    )


def drumParams(mapIndex, baseId):
    row = lambda offset, name, value, memo=None: gsCcm(
        baseId + offset,
        "%s (Map %d)" % (name, mapIndex + 1),
        "41H %02XH #GL" % ((mapIndex << 4) | (offset + 1)),
        "#VL",
        value,
        gate=keyGate,
        memo=memo,
        sync="LastEachGate",
    )
    return folder(
        "GS Drum Setup Map %d" % (mapIndex + 1),
        [
            row(
                0,
                "Play Note Number (pitch coarse)",
                val(0, name="Semitones", **signed64),
                memo="50 cent resolution on SC-88 and later (bank LSB other than 1), 100 cents on SC-55 (LSB 1).",
            ),
            row(
                1,
                "Level",
                val(120),
                "Normalized to 120. Gain is (data/120) squared in 4.4.0 and data/120 in stable builds.",
            ),
            row(2, "Assign Group Number", val(0), "Overrides the exclusive class."),
            row(
                3,
                "Panpot",
                val(64),
                "0 is random. In 4.4.0 a value of 64 leaves the channel pan unchanged.",
            ),
            row(4, "Reverb Send Level", val(127)),
            row(5, "Chorus Send Level", val(0)),
            row(
                6,
                "Rx. Note Off",
                val(0, 0, 1, tableId=tableIds["offOn"]),
                "On forces the drum note to end at Note Off. Off by default.",
            ),
            row(
                7,
                "Rx. Note On",
                val(1, 0, 1, tableId=tableIds["offOn"]),
                "Off disables the drum instrument.",
            ),
            row(8, "Delay Send Level", val(0)),
        ],
    )


def userDrums():
    names = [
        (
            "Play Note Number (pitch coarse)",
            val(0, name="Semitones", minimum=-60, maximum=67, offset=60),
            "Center is 60 for user drums (source subtracts 60).",
        ),
        ("Level", val(120), None),
        ("Assign Group Number", val(0), None),
        ("Panpot", val(64), "0 is random."),
        ("Reverb Send Level", val(127), None),
        ("Chorus Send Level", val(0), None),
        ("Rx. Note Off", val(0, 0, 1, tableId=tableIds["offOn"]), None),
        ("Rx. Note On", val(1, 0, 1, tableId=tableIds["offOn"]), None),
        ("Delay Send Level", val(0), None),
        ("Source Drum Set (map LSB)", val(0), "Bank LSB of the source drum set."),
        ("Source Program", val(0), "Program number of the source drum set."),
        ("Source Note Number", val(36, 0, 127, name="Source Key", kind="Key"), None),
    ]
    sets = []
    for setIndex in range(2):
        items = []
        for index, (name, value, memo) in enumerate(names):
            command = index + 1
            items.append(
                gsCcm(
                    400 + setIndex * 20 + index,
                    "%s (User Set %d)" % (name, setIndex + 1),
                    "21H %02XH #GL" % ((setIndex << 4) | command),
                    "#VL",
                    value,
                    gate=keyGate,
                    memo=experimental(memo or "User drum set parameter."),
                    sync="LastEachGate",
                )
            )
        sets.append(
            folder("User Drum Set %d (Experimental 4.4.0)" % (setIndex + 1), items)
        )
    return folder("GS User Drum Sets (Experimental 4.4.0)", sets)


def buildGs():
    return {
        "tables": buildTables(),
        "items": [
            folder(
                "Roland GS",
                [
                    master(),
                    folder("GS Effects", effects()),
                    part(),
                    folder("GS Drum Setup", [drumParams(0, 380), drumParams(1, 390)]),
                    userDrums(),
                ],
            )
        ],
    }
