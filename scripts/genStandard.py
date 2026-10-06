from lib.ctl import ccm, experimental, folder, val

onOffTable = 1
onOffEntries = [(0, "Off"), (127, "On")]
signed64 = dict(minimum=-64, maximum=63, offset=64)

keyGate = lambda default: val(default, 0, 127, name="Note No.", kind="Key")


def plainCc(ident, name, number, default, memo=None, sync="Last"):
    return ccm(ident, name, "@CC %d #VL" % number, val(default), memo=memo, sync=sync)


def channelControls():
    return folder(
        "Channel Controls",
        [
            plainCc(1, "Modulation Wheel", 1, 0),
            plainCc(
                20,
                "Bank Select MSB",
                0,
                0,
                "Takes effect on the next Program Change. XG drum banks 120, 126 and 127 make the part a drum part.",
            ),
            plainCc(
                21, "Bank Select LSB", 32, 0, "Takes effect on the next Program Change."
            ),
            plainCc(
                5, "Portamento Time", 5, 0, "7 bit only. Time scales with key distance."
            ),
            ccm(7, "Channel Volume", "@CC 7 #VL", val(100), sync="Last"),
            plainCc(8, "Balance", 8, 64),
            ccm(
                10,
                "Pan",
                "@CC 10 #VL",
                val(0, name="Position", **signed64),
                sync="Last",
                memo="Center is 0. Wire value is 64 plus the position.",
            ),
            plainCc(11, "Expression", 11, 127),
            ccm(
                64,
                "Sustain Pedal",
                "@CC 64 #VL",
                val(0, tableId=onOffTable),
                sync="Last",
            ),
            ccm(
                65,
                "Portamento On/Off",
                "@CC 65 #VL",
                val(0, tableId=onOffTable),
                sync="Last",
                memo="On at 64 or above.",
            ),
            plainCc(67, "Soft Pedal", 67, 0, "Lowers the filter cutoff."),
            plainCc(71, "Filter Resonance", 71, 64),
            plainCc(72, "Release Time", 72, 64),
            plainCc(73, "Attack Time", 73, 64),
            plainCc(74, "Brightness", 74, 64),
            plainCc(75, "Decay Time", 75, 64),
            plainCc(76, "Vibrato Rate", 76, 64),
            plainCc(77, "Vibrato Depth", 77, 64),
            plainCc(78, "Vibrato Delay", 78, 64),
            ccm(
                84,
                "Portamento Control",
                "@CC 84 #VL",
                val(0, name="From Key", kind="Key"),
                memo="Sets the key to glide from and forces portamento once, even if portamento is off. In 4.4.0 the value persists across channel reset.",
            ),
            plainCc(91, "Reverb Send", 91, 0, "SpessaSynth defaults reverb to 0."),
            plainCc(93, "Chorus Send", 93, 0),
            plainCc(
                94,
                "Variation Send",
                94,
                0,
                "GS: delay send. XG: variation send, only in system connection (Experimental 4.4.0). Stable builds: GS only.",
            ),
            ccm(
                110,
                "Any Control Change",
                "@CC #GL #VL",
                val(0),
                gate=val(1, 0, 127, name="CC No."),
                memo="Any controller number. CC33 to 63 except 38 are LSB extensions of CC1 to 31.",
            ),
        ],
    )


def channelMode():
    return folder(
        "Channel Mode",
        [
            ccm(
                120,
                "All Sound Off",
                "@CC 120 0",
                memo="Kills all voices, ignoring release.",
            ),
            ccm(121, "Reset All Controllers", "@CC 121 0", memo="RP-15 behavior."),
            ccm(123, "All Notes Off", "@CC 123 0", memo="Respects release."),
            ccm(124, "Omni Mode Off", "@CC 124 0"),
            ccm(125, "Omni Mode On", "@CC 125 0"),
            ccm(
                126,
                "Mono Mode On",
                "@CC 126 #VL",
                val(1),
                memo="Any value switches mono on and terminates active voices on the channel.",
            ),
            ccm(127, "Poly Mode On", "@CC 127 0"),
        ],
    )


def channelMessages():
    return folder(
        "Pitch Bend and Pressure",
        [
            ccm(
                112,
                "Pitch Bend",
                "@PB #VH #VL",
                val(0, -8192, 8191, 8192, name="Bend"),
                memo="Center 0. Range set by the Pitch Bend Range RPN.",
            ),
            ccm(
                113,
                "Channel Pressure",
                "@CP #VL",
                val(0),
                memo="50 cents of vibrato by SF2 default.",
            ),
            ccm(
                114,
                "Poly Key Pressure",
                "@PKP #GL #VL",
                val(0),
                gate=keyGate(60),
                memo="No default behavior. Needs modulators or SysEx.",
            ),
        ],
    )


def rpnControls():
    return folder(
        "RPN",
        [
            ccm(
                130,
                "Pitch Bend Range",
                "@RPN 00H 00H #VL 00H",
                val(2, 0, 24, name="Semitones"),
            ),
            ccm(
                131,
                "Channel Fine Tuning (RPN 0,1)",
                "@RPN 00H 01H #VH #VL",
                val(0, -8192, 8191, 8192, name="100/8192 cents"),
                memo=experimental(
                    "Standard fine tuning RPN. The stable documentation lists fine tuning on RPN 0,3 instead."
                ),
            ),
            ccm(
                132,
                "Channel Fine Tuning (RPN 0,3)",
                "@RPN 00H 03H #VH #VL",
                val(0, -8192, 8191, 8192, name="100/8192 cents"),
                memo="Stable 4.3.x documentation lists this as fine tuning. Non-standard numbering.",
            ),
            ccm(
                133,
                "Channel Coarse Tuning",
                "@RPN 00H 02H #VL #NONE",
                val(0, name="Semitones", **signed64),
            ),
            ccm(
                134,
                "Modulation Depth Range",
                "@RPN 00H 05H #VH #VL",
                val(64, 0, 16383, name="14 bit"),
                memo="Reset value is 64, which is 50 cents. 128 is 100 cents.",
            ),
            ccm(
                135,
                "RPN Null",
                "@CC 101 127 @CC 100 127",
                memo="Resets the selected RPN and NRPN to null. Data entry is then ignored.",
            ),
            ccm(
                136,
                "Any RPN",
                "@RPN #GH #GL #VH #VL",
                val(0, 0, 16383, name="Data 14 bit"),
                gate=val(0, 0, 16383, name="RPN (MSB*128+LSB)"),
                memo="Gate is the 14 bit parameter number. Only 0,0 / 0,1 / 0,2 / 0,3 / 0,5 and 127,127 have effect.",
            ),
        ],
    )


def nrpnControls():
    centered = lambda ident, name, msb, lsb, memo=None: ccm(
        ident, name, "@NRPN %02XH %02XH #VL #NONE" % (msb, lsb), val(64), memo=memo
    )
    customVibrato = experimental(
        "Custom vibrato mode (when enabled) uses these NRPNs directly. Any value other than 64 activates it. Ignored while CC1 is above 0. Stable builds alias CC76 to 78."
    )
    drumGate = val(36, 0, 127, name="Drum Note", kind="Key")
    return folder(
        "NRPN",
        [
            centered(140, "Vibrato Rate (NRPN 1,8)", 1, 0x08, customVibrato),
            centered(141, "Vibrato Depth (NRPN 1,9)", 1, 0x09, customVibrato),
            centered(142, "Vibrato Delay (NRPN 1,10)", 1, 0x0A, customVibrato),
            centered(143, "TVF Cutoff (NRPN 1,32)", 1, 0x20, "Alias of CC74."),
            centered(144, "TVF Resonance (NRPN 1,33)", 1, 0x21, "Alias of CC71."),
            centered(145, "EG Attack (NRPN 1,99)", 1, 0x63, "Alias of CC73."),
            centered(146, "EG Decay (NRPN 1,100)", 1, 0x64, "Alias of CC75."),
            centered(147, "EG Release (NRPN 1,102)", 1, 0x66, "Alias of CC72."),
            folder(
                "Drum NRPN (per note)",
                [
                    ccm(
                        150,
                        "Drum Pitch Coarse",
                        "@NRPN 18H #GL #VL #NONE",
                        val(0, name="Semitones", **signed64),
                        gate=drumGate,
                        memo="GS: 50 cent steps for SC-88 and later banks, 100 cent steps when bank LSB is 1. XG: 100 cent steps.",
                        sync="LastEachGate",
                    ),
                    ccm(
                        151,
                        "Drum Pitch Fine",
                        "@NRPN 19H #GL #VL #NONE",
                        val(0, name="Cents", **signed64),
                        gate=drumGate,
                        memo="XG only.",
                        sync="LastEachGate",
                    ),
                    ccm(
                        152,
                        "Drum Level",
                        "@NRPN 1AH #GL #VL #NONE",
                        val(120),
                        gate=drumGate,
                        memo="120 is normal.",
                        sync="LastEachGate",
                    ),
                    ccm(
                        153,
                        "Drum Pan",
                        "@NRPN 1CH #GL #VL #NONE",
                        val(64),
                        gate=drumGate,
                        sync="LastEachGate",
                        memo="0 is random. 64 leaves the channel pan alone in 4.4.0 (Experimental 4.4.0). Stable builds treat it as absolute pan.",
                    ),
                    ccm(
                        154,
                        "Drum Reverb Send",
                        "@NRPN 1DH #GL #VL #NONE",
                        val(127),
                        gate=drumGate,
                        sync="LastEachGate",
                        memo="Default 0 for kick drums, otherwise 127.",
                    ),
                    ccm(
                        155,
                        "Drum Chorus Send",
                        "@NRPN 1EH #GL #VL #NONE",
                        val(0),
                        gate=drumGate,
                        sync="LastEachGate",
                    ),
                    ccm(
                        156,
                        "Drum Variation Send",
                        "@NRPN 1FH #GL #VL #NONE",
                        val(0),
                        gate=drumGate,
                        sync="LastEachGate",
                        memo="GS and GM: delay send. XG: variation send, system connection only (Experimental 4.4.0).",
                    ),
                ],
            ),
            ccm(
                157,
                "Any NRPN",
                "@NRPN #GH #GL #VL #NONE",
                val(0),
                gate=val(0, 0, 16383, name="NRPN (MSB*128+LSB)"),
                memo="Reaches SF2 NRPN (MSB 120) and the AWE32 compatibility layer. Data MSB only.",
            ),
        ],
    )


sf2Table = 2
sf2Generators = [
    (int(pair.split(" ")[0]), pair.split(" ")[1])
    for pair in "0 startAddrsOffset,1 endAddrsOffset,2 startloopAddrsOffset,3 endloopAddrsOffset,4 startAddrsCoarseOffset,5 modLfoToPitch,6 vibLfoToPitch,7 modEnvToPitch,8 initialFilterFc,9 initialFilterQ,10 modLfoToFilterFc,11 modEnvToFilterFc,12 endAddrsCoarseOffset,13 modLfoToVolume,15 chorusEffectsSend,16 reverbEffectsSend,17 pan,21 delayModLFO,22 freqModLFO,23 delayVibLFO,24 freqVibLFO,25 delayModEnv,26 attackModEnv,27 holdModEnv,28 decayModEnv,29 sustainModEnv,30 releaseModEnv,31 keynumToModEnvHold,32 keynumToModEnvDecay,33 delayVolEnv,34 attackVolEnv,35 holdVolEnv,36 decayVolEnv,37 sustainVolEnv,38 releaseVolEnv,39 keynumToVolEnvHold,40 keynumToVolEnvDecay,45 startloopAddrsCoarseOffset,48 initialAttenuation,50 endloopAddrsCoarseOffset,51 coarseTune,52 fineTune,56 scaleTuning,57 exclusiveClass,58 overridingRootKey".split(
        ","
    )
]

aweC = lambda lo, hi: val(lo, lo, hi, 8192, name="Centered")
aweL = lambda default: val(default, name="LSB")
aweParams = [
    ("Mod LFO Delay", aweC(0, 5900), 1),
    ("Mod LFO Frequency", aweL(0), 0),
    ("Vib LFO Delay", aweC(0, 5900), 1),
    ("Vib LFO Frequency", aweL(0), 0),
    ("Mod Env Delay", aweC(0, 5900), 1),
    ("Mod Env Attack", aweC(0, 5940), 1),
    ("Mod Env Hold", aweC(0, 8191), 1),
    ("Mod Env Decay", aweC(0, 5940), 1),
    ("Mod Env Sustain", aweL(0), 0),
    ("Mod Env Release", aweC(0, 5940), 1),
    ("Vol Env Delay", aweC(0, 5900), 1),
    ("Vol Env Attack", aweC(0, 5940), 1),
    ("Vol Env Hold", aweC(0, 8191), 1),
    ("Vol Env Decay", aweC(0, 5940), 1),
    ("Vol Env Sustain", aweL(0), 0),
    ("Vol Env Release", aweC(0, 5940), 1),
    ("Fine Tune", val(0, -8192, 8191, 8192, name="Centered"), 1),
    ("Mod LFO to Pitch", aweC(-127, 127), 1),
    ("Vib LFO to Pitch", aweC(-127, 127), 1),
    ("Mod Env to Pitch", aweC(-127, 127), 1),
    ("Mod LFO to Volume", aweL(0), 0),
    ("Filter Cutoff", aweL(127), 0),
    ("Filter Q", aweL(0), 0),
    ("Mod LFO to Filter Cutoff", aweC(-64, 63), 1),
    ("Mod Env to Filter Cutoff", aweC(-64, 63), 1),
    ("Chorus Send", aweC(0, 255), 1),
    ("Reverb Send", aweC(0, 255), 1),
]


def generatorNrpn():
    return folder(
        "SF2 Generator NRPN",
        [
            ccm(
                220,
                "SF2 Generator Offset",
                "@NRPN 78H #GL #VH #VL",
                val(0, -8192, 8191, 8192, name="Generator units"),
                gate=val(8, 0, 58, name="Generator", tableId=sf2Table),
                sync="LastEachGate",
                memo="Offsets a soundbank generator on the channel, in that generator's own units. 0 means no change.",
            ),
        ],
    )


def aweNrpn():
    items = []
    for index, (name, value, wide) in enumerate(aweParams):
        data = (
            "@NRPN 7FH %02XH #VH #VL" % index
            if wide
            else "@NRPN 7FH %02XH 00H #VL" % index
        )
        items.append(
            ccm(
                230 + index,
                "AWE32 %s" % name,
                data,
                value,
                memo="SoundBlaster AWE32 NRPN emulation. Replaces the generator value on the channel.",
            )
        )
    return folder("AWE32 NRPN", items)


def systemMessages():
    gm2Reverb = [
        (0, "Small Room"),
        (1, "Medium Room"),
        (2, "Large Room"),
        (3, "Medium Hall"),
        (4, "Large Hall"),
        (8, "Plate"),
    ]
    gm2Chorus = [
        (0, "Chorus 1"),
        (1, "Chorus 2"),
        (2, "Chorus 3"),
        (3, "Chorus 4"),
        (4, "Feedback Chorus"),
        (5, "Flanger"),
    ]
    gpc = (
        lambda slot, param: "@SYSEX F0H 7FH 7FH 04H 05H 01H 01H 01H 01H %02XH %02XH #VL F7H"
        % (slot, param)
    )
    return [
        folder(
            "System Reset and Mode",
            [
                ccm(
                    200,
                    "GM1 System On",
                    "@SYSEX F0H 7EH 7FH 09H 01H F7H",
                    memo="Sets the GM bank system.",
                ),
                ccm(
                    201,
                    "GM System Off",
                    "@SYSEX F0H 7EH 7FH 09H 02H F7H",
                    memo="Resets and returns SpessaSynth to GS mode.",
                ),
                ccm(
                    202,
                    "GM2 System On",
                    "@SYSEX F0H 7EH 7FH 09H 03H F7H",
                    memo="Default bank MSB becomes 121.",
                ),
                ccm(
                    203,
                    "GS Reset",
                    sysex={"profile": "gs", "address": "40H 00H 7FH", "payload": "00H"},
                    memo="DT1 40 00 7F, data 00. Device ID fixed at 10H.",
                ),
                ccm(
                    204,
                    "GS Double Module Mode",
                    sysex={"profile": "gs", "address": "40H 00H 7FH", "payload": "01H"},
                    memo="Resets and makes sure the synth has at least 32 channels.",
                ),
                ccm(
                    205,
                    "XG System On",
                    "@SYSEX F0H 43H 10H 4CH 00H 00H 7EH 00H F7H",
                    memo="Resets and sets XG mode.",
                ),
                ccm(
                    206,
                    "XG All Parameter Reset",
                    "@SYSEX F0H 43H 10H 4CH 00H 00H 7FH 00H F7H",
                    memo="Resets and sets XG mode.",
                ),
            ],
        ),
        folder(
            "Universal Device Control",
            [
                ccm(
                    170,
                    "Master Volume",
                    "@SYSEX F0H 7FH 7FH 04H 01H #VL #VH F7H",
                    val(16383, 0, 16383, name="14 bit"),
                ),
                ccm(
                    171,
                    "Master Balance",
                    "@SYSEX F0H 7FH 7FH 04H 02H #VL #VH F7H",
                    val(8192, 0, 16383, name="14 bit"),
                    memo="8192 is center.",
                ),
                ccm(
                    172,
                    "Master Fine Tuning",
                    "@SYSEX F0H 7FH 7FH 04H 03H #VL #VH F7H",
                    val(0, -8192, 8191, 8192, name="100/8192 cents"),
                ),
                ccm(
                    173,
                    "Master Coarse Tuning",
                    "@SYSEX F0H 7FH 7FH 04H 04H 00H #VL F7H",
                    val(0, name="Semitones", **signed64),
                ),
            ],
        ),
        folder(
            "GM2 Global Parameters",
            [
                ccm(210, "GM2 Reverb Type", gpc(1, 0), val(4, 0, 8, entries=gm2Reverb)),
                ccm(211, "GM2 Reverb Time", gpc(1, 1), val(64), memo="Reverb time."),
                ccm(212, "GM2 Chorus Type", gpc(2, 0), val(2, 0, 5, entries=gm2Chorus)),
                ccm(213, "GM2 Chorus Mod Rate", gpc(2, 1), val(3)),
                ccm(214, "GM2 Chorus Mod Depth", gpc(2, 2), val(19)),
                ccm(215, "GM2 Chorus Feedback", gpc(2, 3), val(8)),
                ccm(216, "GM2 Chorus Send to Reverb", gpc(2, 4), val(0)),
            ],
        ),
        folder(
            "MIDI Tuning Standard",
            [
                ccm(
                    180,
                    "Single Note Tuning Change",
                    "@SYSEX F0H 7FH 7FH 08H 02H 00H 01H #GL #VL 00H 00H F7H",
                    val(60, name="Target Semitone"),
                    gate=val(60, 0, 127, name="Note No.", kind="Key"),
                    memo="Tuning program 0, one note, zero fraction. SpessaSynth treats MTS as realtime.",
                ),
                ccm(
                    181,
                    "Scale Octave Tuning Reset (1 byte, all channels)",
                    "@SYSEX F0H 7FH 7FH 08H 08H 03H 7FH 7FH "
                    + " ".join(["40H"] * 12)
                    + " F7H",
                    memo="All twelve pitch classes set to 0 cents.",
                ),
            ],
        ),
    ]


def buildStandard():
    items = [
        channelControls(),
        channelMode(),
        channelMessages(),
        rpnControls(),
        nrpnControls(),
        generatorNrpn(),
        aweNrpn(),
    ] + systemMessages()
    return {
        "tables": [
            {"id": onOffTable, "entries": dict(onOffEntries)},
            {"id": sf2Table, "entries": dict(sf2Generators)},
        ],
        "items": items,
    }
