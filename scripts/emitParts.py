import argparse
import math
import os
import re
import sys

import yaml

repoDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
partsDir = os.path.join(repoDir, "modules", "spessasynth", "generated", "effectParts")
dataPath = os.path.join(partsDir, "core_data.yaml")

outputPaths = {
    "tables": os.path.join(partsDir, "tables.yaml"),
    "xg/reverb": os.path.join(partsDir, "xg", "reverb.yaml"),
    "xg/chorus": os.path.join(partsDir, "xg", "chorus.yaml"),
    "xg/variation": os.path.join(partsDir, "xg", "variation.yaml"),
    "xg/insertion": os.path.join(partsDir, "xg", "insertion.yaml"),
    "gs/efx": os.path.join(partsDir, "gs", "efx.yaml"),
}

XG_ID_START = 700
GS_ID_START = 950

TABLE_IDS = {
    "lfoRate": 100,
    "filterFreq": 101,
    "eqGain": 102,
    "delayOffset": 103,
    "delaySmall": 104,
    "dryWet": 105,
    "signed": 106,
    "phase": 107,
    "monoStereo": 108,
    "highDamp": 109,
    "inSelect": 110,
    "panDirection": 111,
    "ampType": 112,
    "gsPreDelay": 120,
    "gsDelay1": 121,
    "gsDelay2": 122,
    "gsDelay3": 123,
    "gsDelay4": 124,
    "gsRate1": 125,
    "gsRate2": 126,
    "gsHfDamp": 127,
    "gsCutoff": 128,
    "gsAzimuth": 130,
    "xgReverbType": 140,
    "xgChorusType": 141,
    "xgVariationType": 142,
    "xgInsertionType": 143,
    "gsEfxType": 150,
    "gsControlSource": 151,
}

BLOCK_COLORS = {
    "reverb": "0080E0",
    "chorus": "00B060",
    "variation": "D05090",
    "insertion": "B00060",
    "gs": "B00060",
}


def drop(spec):
    return dict((key, value) for key, value in spec.items() if value is not None)


def val(default=None, minimum=None, maximum=127, offset=None, name=None,
        kind=None, tableId=None, entries=None):
    return drop({
        "default": default,
        "min": minimum,
        "max": maximum,
        "offset": offset,
        "name": name,
        "type": kind,
        "tableId": tableId,
        "entries": entries,
    })


def sym(name, byte):
    return "%s %02XH" % (name, byte)


def wordOf(code):
    return (code >> 8) * 128 + (code & 0xFF)


# Canonically named effect types (from the XG spec)

NAMES = {
    0x0000: "NO EFFECT",
    0x4000: "THRU",
    0x0100: "HALL 1",
    0x0101: "HALL 2",
    0x0106: "HALL M",
    0x0107: "HALL L",
    0x0200: "ROOM 1",
    0x0201: "ROOM 2",
    0x0202: "ROOM 3",
    0x0205: "ROOM S",
    0x0206: "ROOM M",
    0x0207: "ROOM L",
    0x0300: "STAGE 1",
    0x0301: "STAGE 2",
    0x0400: "PLATE",
    0x0407: "GM PLATE",
    0x1000: "WHITE ROOM",
    0x1100: "TUNNEL",
    0x1300: "BASEMENT",
    0x0500: "DELAY L,C,R",
    0x0600: "DELAY L,R",
    0x0700: "ECHO",
    0x0800: "CROSS DELAY",
    0x0900: "EARLY REFLECTION 1",
    0x0901: "EARLY REFLECTION 2",
    0x0A00: "GATE REVERB",
    0x0B00: "REVERSE GATE",
    0x1400: "KARAOKE 1",
    0x1401: "KARAOKE 2",
    0x1402: "KARAOKE 3",
    0x4100: "CHORUS 1",
    0x4101: "CHORUS 2",
    0x4102: "CHORUS 3",
    0x4108: "CHORUS 4",
    0x4103: "GM CHORUS 1",
    0x4104: "GM CHORUS 2",
    0x4105: "GM CHORUS 3",
    0x4106: "GM CHORUS 4",
    0x4107: "FB CHORUS",
    0x4200: "CELESTE 1",
    0x4201: "CELESTE 2",
    0x4202: "CELESTE 3",
    0x4208: "CELESTE 4",
    0x4300: "FLANGER 1",
    0x4301: "FLANGER 2",
    0x4308: "FLANGER 3",
    0x4307: "GM FLANGER",
    0x4400: "SYMPHONIC",
    0x4500: "ROTARY SPEAKER",
    0x4600: "TREMOLO",
    0x4700: "AUTO PAN",
    0x4800: "PHASER 1",
    0x4808: "PHASER 2",
    0x4900: "DISTORTION",
    0x4A00: "OVER DRIVE",
    0x4B00: "AMP SIMULATOR",
    0x4C00: "3 BAND EQ (MONO)",
    0x4D00: "2 BAND EQ (STEREO)",
    0x4E00: "AUTO WAH",
}


def typeName(code, className):
    if code in NAMES:
        return NAMES[code]
    return re.sub(r"([A-Z])", r" \1", className[2:]).strip().upper()


# The hand-authored slot semantics
#
# (slot, name, labelTable key or None, memo). `variation`-block-only slots
# note their memo; slots the converters do not use stay out of the lists.

REVERB_SLOTS = [
    (0, "Reverb Time", None, "Selects the damping of the four delay lines."),
    (1, "Diffusion", "raw", "Sets the allpass spread and the density."),
    (2, "Initial Delay", "delaySmall", "Places the early reflection tap."),
    (3, "HPF Cutoff", "filterFreq", None),
    (4, "LPF Cutoff", "filterFreq", None),
    (9, "Dry/Wet Balance", "dryWet", "Only mixed by the variation connection; system sends stay fully wet."),
    (10, "Reverb Delay", "delaySmall", "Moves the reverb start after the early reflections."),
    (11, "Density", "raw", "Number of density allpasses in use (0 to 3)."),
    (12, "ER/Rev Balance", "raw", "0 = early reflections only, 127 = reverb only."),
    (14, "Feedback Level", "signed", "None at 64."),
]
ROOM_SLOTS = [
    (5, "Width", "raw", None),
    (6, "Height", "raw", None),
    (7, "Depth", "raw", None),
    (8, "Wall Vary", "raw", "Offsets one wall (width, height or depth)."),
]
CHORUS_SLOTS = [
    (0, "LFO Frequency", "lfoRate", None),
    (1, "LFO Depth", "raw", None),
    (2, "Feedback Level", "signed", None),
    (3, "Delay Offset", "delayOffset", None),
    (5, "EQ Low Freq", "filterFreq", None),
    (6, "EQ Low Gain", "eqGain", None),
    (7, "EQ High Freq", "filterFreq", None),
    (8, "EQ High Gain", "eqGain", None),
    (9, "Dry/Wet Balance", "dryWet", "Only mixed by the variation connection."),
    (14, "Input Mode", "monoStereo", "Mono feeds one line for both sides; stereo gives each side its own."),
]
FLANGER_SLOTS = CHORUS_SLOTS + [
    (13, "LFO Phase", "phase", "Phase difference of both chains (64 is none)."),
]
LCR_SLOTS = [
    (0, "Delay L", "raw", "Left tap time in 0.1 ms steps."),
    (1, "Delay C", "raw", "Center tap time in 0.1 ms steps."),
    (2, "Delay R", "raw", "Extra tap time in 0.1 ms steps, scaled by Delay Level."),
    (3, "Feedback Delay", "raw", "Feedback tap time in 0.1 ms steps."),
    (4, "Feedback Level", "signed", None),
    (5, "Delay Level", "raw", "Level of the extra tap."),
    (6, "High Damp", "highDamp", "Roll-off of the repeated taps."),
    (9, "Dry/Wet Balance", "dryWet", None),
]
LR_SLOTS = [
    (0, "Delay L", "raw", "Left tap time in 0.1 ms steps."),
    (1, "Delay R", "raw", "Right tap time in 0.1 ms steps."),
    (2, "Feedback Delay L", "raw", "Left feedback tap time in 0.1 ms steps."),
    (3, "Feedback Delay R", "raw", "Right feedback tap time in 0.1 ms steps."),
    (4, "Feedback Level", "signed", "Both taps take half of the level."),
    (5, "High Damp", "highDamp", None),
    (9, "Dry/Wet Balance", "dryWet", None),
]
ECHO_SLOTS = [
    (0, "Delay L", "raw", "Left line time in 0.1 ms steps."),
    (1, "L Feedback", "signed", None),
    (2, "Delay R", "raw", "Right line time in 0.1 ms steps."),
    (3, "R Feedback", "signed", None),
    (4, "High Damp", "highDamp", None),
    (5, "Delay L 2", "raw", "Second left tap time in 0.1 ms steps."),
    (6, "Delay R 2", "raw", "Second right tap time in 0.1 ms steps."),
    (7, "Delay Level", "raw", "Level of the second taps."),
    (9, "Dry/Wet Balance", "dryWet", None),
]
CROSS_SLOTS = [
    (0, "Delay L", "raw", "One direction's tap time in 0.1 ms steps."),
    (1, "Delay R", "raw", "The other direction's tap time in 0.1 ms steps."),
    (2, "Feedback Level", "signed", "The lines feed back into each other."),
    (3, "Input Select", "inSelect", "Which inputs feed the two lines."),
    (4, "High Damp", "highDamp", None),
    (9, "Dry/Wet Balance", "dryWet", None),
]
DELAY_EQ = [
    (12, "EQ Low Freq", "filterFreq", None),
    (13, "EQ Low Gain", "eqGain", None),
    (14, "EQ High Freq", "filterFreq", None),
    (15, "EQ High Gain", "eqGain", None),
]
LCR_SLOTS = LCR_SLOTS + DELAY_EQ
LR_SLOTS = LR_SLOTS + DELAY_EQ
ECHO_SLOTS = ECHO_SLOTS + DELAY_EQ
CROSS_SLOTS = CROSS_SLOTS + DELAY_EQ
ER_SLOTS = [
    (0, "Pattern", "raw", "Base reflection pattern of the type."),
    (1, "Room Size", "raw", "Scales the pattern delays."),
    (2, "Diffusion", "raw", None),
    (3, "Initial Delay", "delaySmall", None),
    (4, "Feedback Level", "signed", "None at 64."),
    (5, "HPF Cutoff", "filterFreq", None),
    (6, "LPF Cutoff", "filterFreq", None),
    (9, "Dry/Wet Balance", "dryWet", None),
    (10, "Liveness", "raw", "Tilts the reflection gains over time."),
    (11, "Density", "raw", None),
    (12, "High Damp", "highDamp", "Low-pass damping of the reflection loop."),
]
GATE_SLOTS = [
    (0, "Gate Type", "raw", "Gate pattern of the type."),
    (1, "Room Size", "raw", "Scales the pattern delays."),
    (2, "Diffusion", "raw", None),
    (3, "Initial Delay", "delaySmall", None),
    (4, "Feedback Level", "signed", "None at 64."),
    (5, "HPF Cutoff", "filterFreq", None),
    (6, "LPF Cutoff", "filterFreq", None),
    (9, "Dry/Wet Balance", "dryWet", None),
    (10, "Liveness", "raw", "Tilts the reflection gains over time."),
    (11, "Density", "raw", None),
    (12, "High Damp", "highDamp", None),
]
KARAOKE_SLOTS = [
    (0, "Delay", "raw", "Echo time in 0.1 ms steps (see the delay small table)."),
    (1, "Feedback Level", "signed", "None at 64."),
    (2, "HPF Cutoff", "filterFreq", None),
    (3, "LPF Cutoff", "filterFreq", None),
    (9, "Dry/Wet Balance", "dryWet", None),
]
MOD_HEAD = [
    (0, "LFO Frequency", "lfoRate", None),
    (1, "Depth", "raw", None),
]
MOD_TAIL = [
    (5, "EQ Low Freq", "filterFreq", None),
    (6, "EQ Low Gain", "eqGain", None),
    (7, "EQ High Freq", "filterFreq", None),
    (8, "EQ High Gain", "eqGain", None),
    (9, "Dry/Wet Balance", "dryWet", None),
]
SYMPHONIC_SLOTS = MOD_HEAD + [
    (2, "Delay Offset", "delayOffset", "Base delay of the three taps (0.1 ms table)."),
] + MOD_TAIL
ROTARY_SLOTS = MOD_HEAD + MOD_TAIL
TREMOLO_SLOTS = MOD_HEAD + [
    (2, "Pitch Depth", "raw", None),
] + MOD_TAIL[:4] + [
    (13, "LFO Phase", "phase", None),
    (14, "Input Mode", "monoStereo", None),
]
AUTOPAN_SLOTS = MOD_HEAD + [
    (2, "Front/Back Depth", "raw", "Pitch depth of the turning directions."),
    (3, "Pan Direction", "panDirection", None),
] + MOD_TAIL
PHASER1_SLOTS = [
    (0, "LFO Frequency", "raw", None),
    (1, "LFO Depth", "raw", None),
    (2, "LFO Depth 2", "raw", "Mirrored sweep depth parameter."),
    (3, "Feedback Level", "signed", None),
] + MOD_TAIL[:3] + [
    (8, "EQ High Gain", "eqGain", None),
    (9, "Dry/Wet Balance", "dryWet", None),
    (10, "Stage", "raw", "How many allpass stages the outputs take (6 to 10 on Phaser 1, 3 to 5 on Phaser 2)."),
]
PHASER2_SLOTS = [
    (0, "LFO Frequency", "raw", None),
    (1, "LFO Depth", "raw", None),
    (2, "LFO Depth 2", "raw", None),
    (3, "Feedback Level", "signed", None),
] + MOD_TAIL + [
    (10, "Stage", "raw", "How many allpass stages the outputs take (6 to 10 on Phaser 1, 3 to 5 on Phaser 2)."),
    (12, "LFO Phase", "phase", "Phase difference of both chains (64 is none)."),
]
DISTORTION_SLOTS = [
    (0, "Drive", "raw", None),
    (1, "Tone Low Freq", "filterFreq", None),
    (2, "Tone Low Gain", "eqGain", None),
    (3, "LPF Cutoff", "filterFreq", None),
    (4, "Output Level", "raw", "Level compensation of the drive stages."),
    (6, "EQ Mid Freq", "filterFreq", None),
    (7, "EQ Mid Gain", "eqGain", None),
    (8, "EQ Mid Width", "raw", "Peaking EQ width (Q * 10)."),
    (9, "Dry/Wet Balance", "dryWet", None),
    (10, "Edge", "raw", "Gain of the later clipper stages (clip curve)."),
]
AMPSIM_SLOTS = [
    (0, "Drive", "raw", None),
    (1, "Amp Type", "ampType", "Selects the input filters and cabinets."),
    (2, "LPF Cutoff", "filterFreq", None),
    (3, "Output Level", "raw", None),
    (9, "Dry/Wet Balance", "dryWet", None),
    (10, "Edge", "raw", "Gain of the later clipper stages."),
]
EQ3_SLOTS = [
    (0, "EQ Low Gain", "eqGain", None),
    (1, "EQ Mid Freq", "filterFreq", None),
    (2, "EQ Mid Gain", "eqGain", None),
    (3, "EQ Mid Width", "raw", "Peaking EQ width (Q * 10)."),
    (4, "EQ High Gain", "eqGain", None),
    (5, "EQ Low Freq", "filterFreq", None),
    (6, "EQ High Freq", "filterFreq", None),
]
EQ2_SLOTS = [
    (0, "EQ Low Freq", "filterFreq", None),
    (1, "EQ Low Gain", "eqGain", None),
    (2, "EQ High Freq", "filterFreq", None),
    (3, "EQ High Gain", "eqGain", None),
]
AUTOWAH_SLOTS = [
    (0, "LFO Frequency", "lfoRate", None),
    (1, "LFO Depth", "raw", "How far the filter sweeps around the cutoff."),
    (2, "Cutoff", "raw", "Base filter cutoff."),
    (3, "Resonance", "raw", "Filter feedback (10 to 120)."),
] + MOD_TAIL

FAMILY_SLOTS = [
    (re.compile("XG(Hall|Room|Stage|Plate|GMPlate)[A-Za-z0-9]*$"), "plain", REVERB_SLOTS + ROOM_SLOTS),
    (re.compile("XG(WhiteRoom|Tunnel|Basement)$"), "room", REVERB_SLOTS + ROOM_SLOTS),
    (re.compile("XG(GMPlate|GMPlateNo)[0-9]*$"), "plain", REVERB_SLOTS + ROOM_SLOTS),
    (re.compile("XGFlanger|XGGMFlanger"), "flanger", FLANGER_SLOTS),
    (re.compile("XG(Chorus|Celeste|GMChorus)[1-9]?$"), "chorus", CHORUS_SLOTS),
    (re.compile("^XGFBChorus$"), "chorus", CHORUS_SLOTS),
    (re.compile("^XGDelayLCR$"), "lcr", LCR_SLOTS),
    (re.compile("^XGDelayLR$"), "lr", LR_SLOTS),
    (re.compile("^XGEcho$"), "echo", ECHO_SLOTS),
    (re.compile("^XGCrossDelay$"), "cross", CROSS_SLOTS),
    (re.compile("^XGEarlyReflection[12]$"), "er", ER_SLOTS),
    (re.compile("XG(Gate|ReverseGate)Reverb$|^XG(Gate|ReverseGate)$"), "gate", GATE_SLOTS),
    (re.compile("^XGKaraoke"), "karaoke", KARAOKE_SLOTS),
    (re.compile("^XGSymphonic$"), "symphonic", SYMPHONIC_SLOTS),
    (re.compile("^XGRotarySpeaker$"), "rotary", ROTARY_SLOTS),
    (re.compile("^XGTremolo$"), "tremolo", TREMOLO_SLOTS),
    (re.compile("^XGAutoPan$"), "autopan", AUTOPAN_SLOTS),
    (re.compile("^XGPhaser1$"), "phaser1", PHASER1_SLOTS),
    (re.compile("^XGPhaser2$"), "phaser2", PHASER2_SLOTS),
    (re.compile("^XGOverdrive$|^XGDistortion$"), "distortion", DISTORTION_SLOTS),
    (re.compile("^XGAmpSimulator$"), "ampsim", AMPSIM_SLOTS),
    (re.compile("^XGThreeBandEQ$"), "eq3", EQ3_SLOTS),
    (re.compile("^XGTwoBandEQ$"), "eq2", EQ2_SLOTS),
    (re.compile("^XGAutoWah$"), "autowah", AUTOWAH_SLOTS),
]


XG_NO_SLOTS = ("XGNoEffect", "XGThru")


def familyOf(className):
    if className in XG_NO_SLOTS:
        return []
    for pattern, _, slots in FAMILY_SLOTS:
        if pattern.match(className):
            return slots
    raise SystemExit("No slot map for class %s" % className)


# Label tables

def hzLabel(x):
    return "%g kHz" % (x / 1000.0) if x >= 1000 else "%g Hz" % x


def buildXgTables(data):
    labels = data["labels"]
    tables = [
        (
            TABLE_IDS["lfoRate"],
            "[value] Hz",
            [
                (value, "%.2f Hz" % lfoHz(labels, value))
                for value in range(128)
            ],
        ),
        (
            TABLE_IDS["filterFreq"],
            "filter corner in Hz",
            [(index, hzLabel(hz)) for index, hz in enumerate(labels["filterFreq"])],
        ),
        (
            TABLE_IDS["eqGain"],
            "gain in dB",
            [(index, dbLabel(dbOf(labels, index))) for index in range(0, 128)],
        ),
        (
            TABLE_IDS["delayOffset"],
            "0.1 ms steps",
            [
                (value, "%g ms" % (labels["delayOffset"][value] / 10.0))
                for value in range(128)
            ],
        ),
        (
            TABLE_IDS["delaySmall"],
            "0.1 ms steps",
            [
                (value, "%g ms" % (labels["delayTable"][value] / 10.0))
                for value in range(64)
            ],
        ),
        (
            TABLE_IDS["dryWet"],
            None,
            [(0, "Full Dry"), (64, "Center"), (127, "Full Wet")],
        ),
        (
            TABLE_IDS["signed"],
            "the center at 64 is no feedback",
            [(value, "%d (%+d)" % (value, value - 64)) for value in range(1, 128)],
        ),
        (
            TABLE_IDS["phase"],
            "phase difference of the LFOs",
            [
                (value, "%+d deg" % ((value - 64) * 3))
                for value in range(4, 125)
            ],
        ),
        (
            TABLE_IDS["monoStereo"],
            None,
            [(0, "Mono"), (1, "Stereo")],
        ),
        (
            TABLE_IDS["highDamp"],
            "damping low-pass corner (0 is Thru)",
            [
                (index, highDampLabel(labels, index))
                for index in range(len(labels["highDampFrequency"]))
            ],
        ),
        (
            TABLE_IDS["inSelect"],
            None,
            [(0, "L"), (1, "R"), (2, "L&R")],
        ),
        (
            TABLE_IDS["panDirection"],
            None,
            [(0, "L<->R"), (1, "L->R"), (2, "L<-R"), (3, "L turn"), (4, "R turn"), (5, "L/R")],
        ),
        (
            TABLE_IDS["ampType"],
            None,
            [(0, "Off"), (1, "Stack"), (2, "Combo"), (3, "Tube")],
        ),
    ]
    return tables


def lfoHz(labels, value):
    word = labels["lfoRate"][value]
    mode = labels["coefficientModes"][9]
    return numberFromWord(word, mode) * 22050


def numberFromWord(word, mode):
    if mode == 2:
        exponent = word >> 7
        mantissa = word & 0x7F
        return (1 << exponent) * 2.384185791015625e-7 * mantissa
    signed = word - 1024 if word > 512 else word
    return signed / (128.0 if mode == 1 else 512.0)


def dbOf(labels, index):
    return 20.0 * math.log10(max(labels["filterGain"][index], 1e-12))


def dbLabel(db):
    if abs(db) < 0.05:
        return "0 dB"
    sign = "+" if db > 0 else "-"
    return "%s%d dB" % (sign, abs(round(db)))


def highDampLabel(labels, index):
    hz = labels["filterFreq"][labels["highDampFrequency"][index]]
    if hz <= 0:
        return "Thru"
    return hzLabel(hz)


def buildGsTables(data):
    conv = data["labels"]["gsConversion"]
    gsHz = lambda v: "%g Hz" % v if v > 0 else "Thru"
    return [
        (
            TABLE_IDS["gsPreDelay"],
            "pre delay in ms",
            [(v, "%g ms" % conv[v][0]) for v in range(128)],
        ),
        (
            TABLE_IDS["gsDelay1"],
            "delay 1 in ms",
            [(v, "%g ms" % (conv[v][1] / 10.0)) for v in range(128)],
        ),
        (
            TABLE_IDS["gsDelay2"],
            "delay 2 in ms",
            [(v, "%g ms" % (conv[v][2] / 10.0)) for v in range(128)],
        ),
        (
            TABLE_IDS["gsDelay3"],
            "delay 3 in ms",
            [(v, "%g ms" % conv[v][3]) for v in range(128)],
        ),
        (
            TABLE_IDS["gsDelay4"],
            "delay 4 in ms",
            [(v, "%g ms" % (conv[v][4] / 10.0)) for v in range(128)],
        ),
        (
            TABLE_IDS["gsRate1"],
            "rate 1 in Hz",
            [(v, "%.2f Hz" % conv[v][5]) for v in range(128)],
        ),
        (
            TABLE_IDS["gsRate2"],
            "rate 2 in Hz",
            [(v, "%.2f Hz" % conv[v][6]) for v in range(128)],
        ),
        (
            TABLE_IDS["gsHfDamp"],
            "HF damp corner, 120+ bypass",
            [(v, gsHz(conv[v][7])) for v in range(128)],
        ),
        (
            TABLE_IDS["gsCutoff"],
            "tone filter corner in Hz",
            [(v, hzLabel(conv[v][8])) for v in range(128)],
        ),
        (
            TABLE_IDS["gsAzimuth"],
            "azimuth in degrees",
            [(v, "%g deg" % conv[v][12]) for v in range(128)],
        ),
        (
            TABLE_IDS["gsControlSource"],
            "EFX control source (CC 1-95, aftertouch, pitch bend)",
            [(0, "Off")]
            + [(v, "CC %d" % v) for v in range(1, 96)]
            + [(0x70, "Channel Aftertouch"), (0x71, "Pitch Bend")],
        ),
    ]


def buildTables(data):
    tables = buildXgTables(data) + buildGsTables(data)
    helpers = [
        ("reverb", ["xg", "reverb"]),
        ("chorus", ["xg", "chorus"]),
        ("variation", ["xg", "variation"]),
        ("insertion", ["xg", "insertion"]),
    ]
    for key, path in helpers:
        specs = getByPath(data, path)["types"]
        tables.append(
            (
                TABLE_IDS["xg" + key[0].upper() + key[1:] + "Type"],
                "effect type selects",
                [
                    (wordOf(spec["code"]), typeName(spec["code"], spec["class"]))
                    for spec in specs
                ],
            )
        )
    efxTypes = [(wordOf(g["code"]), g["name"]) for g in data["gs"]["types"]]
    tables.append(
        (TABLE_IDS["gsEfxType"], "GS EFX types", efxTypes)
    )
    return tables


def getByPath(data, path):
    for step in path:
        data = data[step]
    return data


# The XG family blocks

XG_BLOCKS = [
    ("reverb", "XG Reverb"),
    ("chorus", "XG Chorus"),
    ("variation", "XG Variation"),
    ("insertion", "XG Insertion Effects"),
]


INSERTION_GATE = (1, 4, -1, "Insertion No.")


def partOrOff():
    return val(128, 1, 128, -1, kind=None, tableId=27, entries=None)


# System level parameters of every block. (name, address byte, default).
XG_SYSTEM = {
    "reverb": [
        ("Reverb Return", 0x0C, 64),
        ("Reverb Pan", 0x0D, 64),
    ],
    "chorus": [
        ("Chorus Return", 0x2C, 64),
        ("Chorus Pan", 0x2D, 64),
        ("Chorus Send To Reverb", 0x2E, 0),
    ],
    "variation": [
        ("Variation Return", 0x56, 64),
        ("Variation Pan", 0x57, 64),
        ("Variation Send To Reverb", 0x58, 0),
        ("Variation Send To Chorus", 0x59, 0),
    ],
}

SYSTEM_MEMOS = {
    0x2E: "Applies when the chorus is a system connection.",
    0x59: "Amount of the variation input also fed into the chorus.",
    0x58: "Amount of the variation input also fed into the reverb.",
}


def slotAddress(blockKey, slot, wide):
    if blockKey == "reverb":
        byte = 0x10 + slot - 10 if slot > 9 else 0x02 + slot
        return "02H 01H %02XH" % byte
    if blockKey == "chorus":
        byte = 0x30 + slot - 10 if slot > 9 else 0x22 + slot
        return "02H 01H %02XH" % byte
    if blockKey == "variation":
        if slot > 9:
            return "02H 01H %02XH" % (0x70 + slot - 10)
        return "02H 01H %02XH" % (0x42 + 2 * slot)
    if slot > 9:
        return "03H #GL %02XH" % (0x20 + slot - 10)
    if wide:
        return "03H #GL %02XH" % (0x30 + 2 * slot)
    return "03H #GL %02XH" % (0x02 + slot)


def gateValue(minimum, maximum, offset, name):
    return val(None, minimum, maximum, offset, name=name)


class Counter:
    def __init__(self, start):
        self.value = start

    def take(self):
        self.value += 1
        return self.value


def widePayload(blockKey, low, high):
    if blockKey == "variation" and low <= 9:
        return True
    if blockKey == "insertion" and low <= 9 and high > 127:
        return True
    return False


def fallbackRange(data, paramName, tableKey):
    labels = data["labels"]
    if tableKey == "signed":
        return [1, 127]
    if tableKey == "phase":
        return [4, 124]
    if tableKey == "monoStereo":
        return [0, 1]
    if tableKey == "delaySmall":
        return [0, 63]
    if tableKey == "highDamp":
        return [0, len(labels["highDampFrequency"]) - 1]
    if tableKey == "filterFreq":
        return [0, len(labels["filterFreq"]) - 1]
    if paramName == "Density":
        return [0, 3]
    return [0, 127]


def buildXgBlock(data, blockKey, blockName, counter):
    parent = data["xg"][blockKey]
    isInsertion = blockKey == "insertion"
    gate = (gateValue(*INSERTION_GATE) if isInsertion else None)
    sync = "LastEachGate" if isInsertion else "Last"
    if isInsertion:
        typeAddress = "03H #GL 00H"
    else:
        typeAddresses = {"reverb": "02H 01H 00H", "chorus": "02H 01H 20H"}
        typeAddress = typeAddresses.get(blockKey, "02H 01H 40H")
    kindName = blockKey[0].upper() + blockKey[1:]
    typeTable = TABLE_IDS["xg%sType" % kindName]
    maxWord = max(wordOf(spec["code"]) for spec in parent["types"])
    typeSelect = ccm(
        counter.take(),
        "%s Type" % blockName,
        value=val(
            wordOf(parent["defaultType"]), 0, maxWord, tableId=typeTable
        ),
        gate=gate,
        sysex={"address": typeAddress, "payload": "#VH #VL"},
        memo="Value is MSB*128+LSB. " + TYPE_MEMO.get(blockKey, ""),
        sync=sync,
    )
    items = [typeSelect]
    for name, byte, specDefault in XG_SYSTEM.get(blockKey, []):
        items.append(
            ccm(
                counter.take(),
                name,
                value=val(specDefault, 0, 127),
                sysex={"address": "02H 01H %02XH" % byte, "payload": "#VL"},
                memo=SYSTEM_MEMOS.get(byte),
                sync=sync,
            )
        )
    if blockKey == "variation":
        items.append(
            ccm(
                counter.take(),
                "Variation Connection",
                value=val(0, 0, 1, tableId=22),
                sysex={"address": "02H 01H 5AH", "payload": "#VL"},
                memo="Insertion routes one part through the effect. "
                + "System makes it a send effect.",
                sync=sync,
            )
        )
        items.append(
            ccm(
                counter.take(),
                "Variation Part Number",
                value=partOrOff(),
                sysex={"address": "02H 01H 5BH", "payload": "#VL"},
                memo="Used in insertion connection. 128 is Off (wire 127).",
                sync=sync,
            )
        )
    if blockKey == "insertion":
        items.append(
            ccm(
                counter.take(),
                "Insertion Part Number",
                value=partOrOff(),
                gate=gate,
                sysex={"address": "03H #GL 0CH", "payload": "#VL"},
                memo="128 is Off (wire 127).",
                sync=sync,
            )
        )
    # One parameter CCM per distinct (slot, name, table) shape; its range is
    # the union of the ranges every type using the slot has for the slot.
    shapes = {}
    for spec in parent["types"]:
        for slotNo, paramName, tableKey, memo in familyOf(spec["class"]):
            extra = spec["ranges"].get(str(slotNo))
            if extra is None:
                extra = fallbackRange(data, paramName, tableKey)
            key = (slotNo, paramName, tableKey)
            low, high = extra
            if key not in shapes:
                shapes[key] = [low, high, None, memo]
            else:
                shapes[key][0] = min(shapes[key][0], low)
                shapes[key][1] = max(shapes[key][1], high)
            specDefault = spec["defaults"][slotNo]
            if shapes[key][2] is None:
                shapes[key][2] = specDefault
    params = []
    shapeIds = {}
    for key in sorted(shapes):
        slotNo, paramName, tableKey = key
        low, high, specDefault, memo = shapes[key]
        wide = widePayload(blockKey, slotNo, high)
        if not wide and high > 127:
            raise SystemExit("7-bit slot out of range: %s %s" % (blockKey, paramName))
        identifier = counter.take()
        shapeIds[key] = identifier
        params.append(
            ccm(
                identifier,
                paramName,
                value=val(
                    specDefault,
                    low,
                    high,
                    tableId=(TABLE_IDS.get(tableKey) if tableKey else None),
                ),
                gate=gate,
                sysex={
                    "address": slotAddress(blockKey, slotNo, wide),
                    "payload": ("#VH #VL" if wide else "#VL"),
                },
                memo=memo,
                sync=sync,
            )
        )
    typeFolders = []
    for spec in parent["types"]:
        typeCode = spec["code"]
        links = []
        for slotNo, paramName, tableKey, memo in familyOf(spec["class"]):
            key = (slotNo, paramName, tableKey)
            links.append(
                {
                    "type": "ccmLink",
                    "id": shapeIds[key],
                    "value": spec["defaults"][slotNo],
                    "gate": gate,
                }
            )
        if links:
            typeFolders.append(
                folder(typeName(typeCode, spec["class"]), links)
            )
    items.extend(params)
    items.append(folder("Types", typeFolders))
    return folder(blockName, items)


TYPE_MEMO = {
    "reverb": "Types the synth lacks are silent.",
    "chorus": "Types the synth lacks are silent.",
    "variation": "Types the synth lacks pass dry.",
    "insertion": "Types the synth lacks pass dry.",
}


def ccm(identifier, name, value, gate=None, sysex=None, memo=None, sync="Last"):
    spec = {
        "type": "ccm",
        "id": identifier,
        "name": name,
        "value": value,
        "gate": gate,
        "sync": sync,
        "memo": memo,
        "sysex": sysex,
    }
    return dict((key, item) for key, item in spec.items() if item is not None)


def folder(name, items):
    return {"type": "folder", "name": name, "items": items}


def buildXg(data, counter):
    return {
        "xg/" + blockKey: buildXgBlock(data, blockKey, blockName, counter)
        for blockKey, blockName in XG_BLOCKS
    }


# The GS insertion effect (EFX)

GS_PARAM_COUNT = 20

# (address byte, default, minimum, maximum, name). Addresses past the EFX
# parameters: send levels and the two control source/depth pairs.
FX_CONTROL = [
    (0x17, 40, 0, 127, "Send Level to Reverb"),
    (0x18, 0, 0, 127, "Send Level to Chorus"),
    (0x19, 0, 0, 127, "Send Level to Delay"),
    (0x1B, 0, 0, 127, "Control Source 1"),
    (0x1C, 64, 0, 127, "Control Depth 1"),
    (0x1D, 0, 0, 127, "Control Source 2"),
    (0x1E, 64, 0, 127, "Control Depth 2"),
]

FX_TABLES = {
    0x1B: "gsControlSource",
    0x1D: "gsControlSource",
}

FX_MEMOS = {
    0x17: "How much of the EFX output also goes into the reverb block. "
    "A type change resets it to 40.",
    0x18: "How much of the EFX output also goes into the chorus block. "
    "A type change resets it to 0.",
    0x19: "How much of the EFX output also goes into the delay block. "
    "A type change resets it to 0.",
    0x1B: "Controller that modulates the type's first controlled parameter: "
    "0 is none, 1 to 95 is CC 1-95, 112 is channel aftertouch, 113 pitch bend.",
    0x1C: "How far the control source 1 moves, signed around 64 (zero at 64).",
    0x1D: "Controller that modulates the type's second controlled parameter.",
    0x1E: "How far the control source 2 moves, signed around 64 (zero at 64).",
}


def gsAddress(slot):
    return "40H 03H %02XH" % slot if slot else "40H 03H 00H"


def buildGsEfx(data, counter):
    gsTypes = data["gs"]["types"]
    maxWord = max(wordOf(g["code"]) for g in gsTypes if g["code"] is not None)
    items = [
        ccm(
            counter.take(),
            "EFX Type",
            value=val(0, 0, maxWord, tableId=TABLE_IDS["gsEfxType"]),
            sysex={"address": gsAddress(0), "payload": "#VH #VL"},
            memo="Value is MSB*128+LSB. A type change resets the parameters and the "
            + "send levels (reverb 40, chorus 0, delay 0); the control sources "
            + "stay. Codes the synth lacks pass dry (Thru).",
        )
    ]
    # One parameter CCM per distinct (slot, minimum, maximum) shape. The
    # parameters' meaning depends on the type, so the names stay plain and
    # every type folder supplies its own defaults through ccmLinks.
    # The parameter limits and minimums use the synth's zero based indices.
    shapes = {}
    for spec in gsTypes:
        for index in range(GS_PARAM_COUNT):
            low = spec["minimums"].get(index, 0)
            high = spec["limits"].get(index, 127)
            key = (index, low, high)
            if key not in shapes:
                shapes[key] = [True, spec["defaults"][index]]
    shapeIds = {}
    for key in sorted(shapes):
        index, low, high = key
        identifier = counter.take()
        shapeIds[key] = identifier
        items.append(
            ccm(
                identifier,
                "EFX Parameter %d" % (index + 1),
                value=val(shapes[key][1], low, high),
                sysex={"address": gsAddress(index + 3), "payload": "#VL"},
                memo="Meaning depends on the EFX type; the type folder "
                + "under Types lists the defaults of every type.",
            )
        )
    items.extend(
        ccm(
            counter.take(),
            name,
            value=val(
                specDefault,
                minimum,
                maximum,
                tableId=TABLE_IDS.get(FX_TABLES.get(byte)),
            ),
            sysex={"address": gsAddress(byte), "payload": "#VL"},
            memo=FX_MEMOS[byte],
        )
        for byte, specDefault, minimum, maximum, name in FX_CONTROL
    )
    typeFolders = []
    for spec in gsTypes:
        if spec["code"] is None:
            continue
        typeLinks = [
            {
                "type": "ccmLink",
                "id": items[0]["id"],
                "value": wordOf(spec["code"]),
            }
        ]
        for index in range(GS_PARAM_COUNT):
            low = spec["minimums"].get(index, 0)
            high = spec["limits"].get(index, 127)
            typeLinks.append(
                {
                    "type": "ccmLink",
                    "id": shapeIds[(index, low, high)],
                    "value": spec["defaults"][index],
                }
            )
        typeFolders.append(folder(spec["name"], typeLinks))
    items.append(folder("Types", typeFolders))
    return folder("GS Insertion Effect (EFX)", items)


# Top level

def tableNode(identifier, entries):
    return {"id": identifier, "entries": dict(entries)}


def checkSlotCoverage(data):
    missing = set()
    for blockKey, _ in XG_BLOCKS:
        for spec in data["xg"][blockKey]["types"]:
            named = set(slot[0] for slot in familyOf(spec["class"]))
            for slotNo in spec["ranges"]:
                if int(slotNo) not in named:
                    missing.add((blockKey, spec["class"], int(slotNo)))
    if missing:
        raise SystemExit(
            "Slots with a synth range but no entry in a slot list: "
            + ", ".join("%s %s #%d" % item for item in sorted(missing))
        )


def build():
    with open(dataPath, encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    checkSlotCoverage(data)
    documents = {}
    # The parts include into the module files directly: tables.yaml must be
    # a bare list of table nodes, the block files a single folder item each.
    documents["tables"] = [
        tableNode(identifier, entries)
        for identifier, _, entries in buildTables(data)
    ]
    documents.update(buildXg(data, Counter(XG_ID_START)))
    documents["gs/efx"] = buildGsEfx(data, Counter(GS_ID_START))
    return documents


def documentText(document):
    return yaml.dump(
        document,
        Dumper=yaml.SafeDumper,
        sort_keys=False,
        width=10000,
        allow_unicode=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify",
                        default=False)
    choices = parser.parse_args()
    documents = build()
    for name, document in sorted(documents.items()):
        text = documentText(document)
        target = outputPaths[name]
        if choices.check:
            if not os.path.exists(target):
                raise SystemExit("%s is missing. Run: python scripts/emitParts.py" % name)
            with open(target, encoding="utf-8") as stream:
                current = stream.read()
            if current != text:
                raise SystemExit("%s is stale. Run: python scripts/emitParts.py" % name)
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(text)
            print("wrote %s" % os.path.relpath(target))
    print("emitParts: %d documents" % len(documents))


if __name__ == "__main__":
    main()
