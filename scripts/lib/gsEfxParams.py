# Value tables. Entries are built by buildTables(); ids sit above the
# existing GS ids (120-130, 150-151) and the XG ids (140-143).

TABLE_IDS = {
    "gsEqFreq": 160,
    "gsLpf": 161,
    "gsManual": 162,
    "gsAccel": 163,
    "gsGain": 164,
    "gsPan": 165,
    "gsOnOff": 166,
    "gsFeedback": 167,
    "gsPhase": 168,
    "gsPitchCoarse": 169,
    "gsPitchFine": 170,
    "gsWave": 171,
    "gsAmp": 172,
    "gsDriveType": 173,
    "gsFilter3": 174,
    "gsFilter2": 175,
    "gsPolarity": 176,
    "gsModType": 177,
    "gsOutput": 178,
    "gsFbMode": 179,
    "gsPhaseInv": 180,
    "gsVowel": 181,
    "gsReverbType": 182,
    "gsGateType": 183,
    "gsPitchMode": 184,
    "gsEqQ": 185,
    "gsLimiterRatio": 186,
    "gsPostGain": 187,
    "gsDisc": 188,
    "gsHum": 189,
    "gsNoise": 190,
    "gsOneBased": 191,
    "gsSpeed": 192,
    "gsGateTime": 193,
    "gsSigned": 194,
    "gsCwDirection": 195,
    "gsTremoloType": 196,
    "gsEqLowFreq": 197,
    "gsEqHighFreq": 198,
    "gsMonoStereo": 108,
}


def enum(*names):
    return [(index, name) for index, name in enumerate(names)]


def buildTables(conv):
    """Returns [(id, comment, [(value, label)])] for every new GS EFX table."""
    ids = TABLE_IDS

    def column(index, fmt):
        return [(v, fmt(conv[v][index])) for v in range(128)]

    def hz(value):
        return "%g Hz" % value if value < 1000 else "%g kHz" % (value / 1000.0)

    def pan(v):
        if v == 64:
            return "Center"
        return "L%d" % (64 - v if v else 63) if v < 64 else "R%d" % (v - 64)

    return [
        (ids["gsEqFreq"], "EQ mid frequency", column(9, hz)),
        (ids["gsLpf"], "low pass corner", column(10, hz)),
        (ids["gsManual"], "manual (phaser / wah) frequency", column(11, hz)),
        (ids["gsAccel"], "time control delay acceleration step", column(13, lambda x: "%g" % x)),
        (
            ids["gsGain"],
            "EQ gain, the manual's range is 52-76 (-12 to +12 dB)",
            [(v, "%+d dB" % (v - 64) if v != 64 else "0 dB") for v in range(52, 77)],
        ),
        (ids["gsPan"], "pan", [(v, pan(v)) for v in range(128)]),
        (ids["gsOnOff"], None, enum("Off", "On")),
        (
            ids["gsFeedback"],
            "feedback, 15 to 113 is -98 to +98 % in 2 % steps",
            [(v, "%+d %%" % ((v - 64) * 2)) for v in range(15, 114)],
        ),
        (
            ids["gsPhase"],
            "LFO phase, 2 degrees per step up to 180",
            [(v, "%d deg" % min(180, v * 2)) for v in range(91)],
        ),
        (
            ids["gsPitchCoarse"],
            "pitch shifter coarse, -24 to +12 semitones",
            [(v, "%+d st" % (v - 64) if v != 64 else "0 st") for v in range(40, 77)],
        ),
        (
            ids["gsPitchFine"],
            "pitch shifter fine, -100 to +100 cents",
            [(v, "%+d cents" % ((v - 64) * 2) if v != 64 else "0 cents") for v in range(14, 115)],
        ),
        (ids["gsWave"], "LFO wave", enum("Triangle", "Square", "Sine", "Saw Up", "Saw Down")),
        (ids["gsAmp"], "amp simulator type", enum("Small", "Built-In", "2-Stack", "3-Stack")),
        (ids["gsDriveType"], None, enum("Overdrive", "Distortion")),
        (ids["gsFilter3"], None, enum("Off", "LPF", "HPF")),
        (ids["gsFilter2"], None, enum("LPF", "BPF")),
        (ids["gsPolarity"], None, enum("Down", "Up")),
        (ids["gsModType"], None, enum("Chorus", "Flanger")),
        (ids["gsOutput"], None, enum("Speaker", "Phones")),
        (ids["gsFbMode"], None, enum("Normal", "Cross")),
        (ids["gsPhaseInv"], None, enum("Normal", "Invert")),
        (ids["gsVowel"], None, enum("a", "i", "u", "e", "o")),
        (ids["gsReverbType"], None, enum("Room 1", "Room 2", "Stage 1", "Stage 2", "Hall 1", "Hall 2")),
        (ids["gsGateType"], None, enum("Normal", "Reverse", "Sweep 1", "Sweep 2")),
        (ids["gsPitchMode"], "pitch shifter mode (window)", enum("Mode 1", "Mode 2", "Mode 3", "Mode 4", "Mode 5")),
        (ids["gsEqQ"], "EQ Q", enum("0.5", "1.0", "2.0", "4.0", "9.0")),
        (ids["gsLimiterRatio"], None, enum("1.5:1", "2:1", "4:1", "100:1")),
        (ids["gsPostGain"], None, enum("0 dB", "+6 dB", "+12 dB", "+18 dB")),
        (ids["gsDisc"], None, enum("LP", "EP", "SP", "RND")),
        (ids["gsHum"], None, enum("50 Hz", "60 Hz")),
        (ids["gsNoise"], None, enum("White", "Pink")),
        (ids["gsOneBased"], "shown as 1 based", [(v, str(v + 1)) for v in range(128)]),
        (ids["gsSpeed"], "rotary speed", [(v, "Slow" if v < 64 else "Fast") for v in range(128)]),
        (
            ids["gsGateTime"],
            "gate time, 5 ms steps (values above 99 act as 99)",
            [(v, "%d ms" % (5 * (v + 1))) for v in range(100)],
        ),
        (
            ids["gsSigned"],
            "deviation, 44 to 84 is -20 to +20",
            [(v, "%+d" % (v - 64) if v != 64 else "0") for v in range(44, 85)],
        ),
        (ids["gsCwDirection"], None, enum("Counter-clockwise", "Clockwise")),
        (ids["gsTremoloType"], None, enum("Tremolo", "Auto Pan")),
        (ids["gsEqLowFreq"], None, [(0, "200 Hz"), (1, "400 Hz")]),
        (ids["gsEqHighFreq"], None, [(0, "4 kHz"), (1, "8 kHz")]),
    ]


# Kinds: key -> (display name, table key, memo)

def K(name, table=None, memo=None):
    return (name, table, memo)


KINDS = {
    "level": K("Level", None, "Output level of the effect."),
    "plain": K("Value"),
    "pan": K("Pan", "gsPan"),
    "balance": K("Effect Balance", None, "0 is dry only, 127 is effect only."),
    "lowGain": K("Low Gain", "gsGain", "Low shelf gain. 64 is flat."),
    "highGain": K("High Gain", "gsGain", "High shelf gain. 64 is flat."),
    "preDelay": K("Pre Delay", "gsPreDelay"),
    "rate1": K("Rate", "gsRate1"),
    "rate2": K("Rate", "gsRate2"),
    "depth": K("Depth"),
    "feedback": K("Feedback", "gsFeedback", "64 is no feedback."),
    "hfDamp": K("HF Damp", "gsHfDamp", "Lowers the repeats' high end. 120 and above is bypass."),
    "delay1": K("Delay Time", "gsDelay1"),
    "delay2": K("Delay Time", "gsDelay2"),
    "delay3": K("Delay Time", "gsDelay3"),
    "delay4": K("Delay Time", "gsDelay4"),
    "phase": K("Phase", "gsPhase"),
    "wave": K("Wave", "gsWave"),
    "amp": K("Amp Type", "gsAmp"),
    "ampSwitch": K("Amp Switch", "gsOnOff"),
    "driveType": K("Drive Type", "gsDriveType"),
    "drive": K("Drive"),
    "driveSwitch": K("Drive Switch", "gsOnOff"),
    "eqFreq": K("Mid Frequency", "gsEqFreq"),
    "eqQ": K("Mid Q", "gsEqQ"),
    "eqGain": K("Mid Gain", "gsGain"),
    "modType": K("Chorus / Flanger", "gsModType"),
    "output": K("Output", "gsOutput"),
    "monoStereo": K("Mono / Stereo", "gsMonoStereo"),
    "coarse": K("Pitch Coarse", "gsPitchCoarse"),
    "fine": K("Pitch Fine", "gsPitchFine"),
    "pitchMode": K("Pitch Mode", "gsPitchMode", "Larger modes use a shorter window."),
    "cutoff": K("Cutoff", "gsCutoff"),
    "manual": K("Manual", "gsManual"),
    "filter3": K("Filter Type", "gsFilter3"),
    "filter2": K("Filter Type", "gsFilter2"),
    "compSustain": K("Comp Sustain"),
    "compAttack": K("Comp Attack"),
    "compLevel": K("Comp Level"),
    "compSwitch": K("Comp Switch", "gsOnOff"),
    "rotSlow": K("Slow Rate", "gsRate1"),
    "rotFast": K("Fast Rate", "gsRate1"),
    "rotAccel": K("Acceleration"),
    "rotLevel": K("Rotor Level"),
    "separation": K("Separation"),
    "speed": K("Speed", "gsSpeed", "0-63 slow, 64-127 fast."),
    "azimuth": K("Azimuth", "gsAzimuth"),
}


def P(slot, kind, name=None, table=None, memo=None):
    """One parameter: slot (1 based), kind key, optional overrides."""
    base = KINDS[kind] if isinstance(kind, str) else kind
    return (
        slot,
        name or base[0],
        table if table is not None else base[1],
        memo if memo is not None else base[2],
    )


def common(gains=True, pan=False, balance=True, level=True):
    """The shared tail of most types: balance (16), gains (17/18), pan (19), level (20)."""
    rows = []
    if balance:
        rows.append(P(16, "balance"))
    if gains:
        rows += [P(17, "lowGain"), P(18, "highGain")]
    if pan:
        rows.append(P(19, "pan"))
    if level:
        rows.append(P(20, "level"))
    return rows


def twoStage(first, second, balanceSlot=10, gains=True):
    """Series combinations: first stage 1-5, second stage 6-10."""
    rows = list(first) + list(second)
    if gains:
        rows += [P(17, "lowGain"), P(18, "highGain")]
    rows.append(P(20, "level"))
    return rows


def chorusStage(base=1):
    return [
        P(base, "preDelay", "Chorus Pre Delay"),
        P(base + 1, "rate1", "Chorus Rate"),
        P(base + 2, "depth", "Chorus Depth"),
        P(base + 4, "balance", "Chorus Balance"),
    ]


def flangerStage(base=1):
    return [
        P(base, "preDelay", "Flanger Pre Delay"),
        P(base + 1, "rate1", "Flanger Rate"),
        P(base + 2, "depth", "Flanger Depth"),
        P(base + 3, "feedback", "Flanger Feedback"),
        P(base + 4, "balance", "Flanger Balance"),
    ]


def delayStage(base=6, balanceSlot=10):
    return [
        P(base, "delay3", "Delay Time"),
        P(base + 1, "feedback", "Delay Feedback"),
        P(base + 2, "hfDamp", "Delay HF Damp"),
        P(balanceSlot, "balance", "Delay Balance"),
    ]


def chorusSecond():
    return [
        P(6, "preDelay", "Chorus Pre Delay"),
        P(7, "rate1", "Chorus Rate"),
        P(8, "depth", "Chorus Depth"),
        P(10, "balance", "Chorus Balance"),
    ]


def flangerSecond():
    return [
        P(6, "preDelay", "Flanger Pre Delay"),
        P(7, "rate1", "Flanger Rate"),
        P(8, "depth", "Flanger Depth"),
        P(9, "feedback", "Flanger Feedback"),
        P(10, "balance", "Flanger Balance"),
    ]


def driveBlock(prefix=""):
    """OD / DS -> X: slots 1-4 (drive, drive pan, amp type, amp switch)."""
    return [
        P(1, "drive", prefix + "Drive"),
        P(2, "pan", prefix + "Drive Pan"),
        P(3, "amp"),
        P(4, "ampSwitch"),
    ]


def enhancerBlock():
    return [
        P(1, "plain", "Enhancer Sensitivity", memo="How strongly high frequencies are enhanced."),
        P(2, "plain", "Enhancer Mix Level"),
    ]


def driveTail(second):
    return list(second) + [P(17, "lowGain"), P(18, "highGain"), P(20, "level")]


def parallelPans(first, second):
    return [
        P(16, "pan", first + " Pan"),
        P(17, "plain", first + " Level"),
        P(18, "pan", second + " Pan"),
        P(19, "plain", second + " Level"),
        P(20, "level"),
    ]


def odBlock(offset=0, prefix=""):
    return [
        P(1 + offset, "driveType", prefix + "Drive Type"),
        P(2 + offset, "drive", prefix + "Drive"),
        P(3 + offset, "amp", prefix + "Amp Type"),
        P(4 + offset, "ampSwitch", prefix + "Amp Switch"),
    ]


def rotaryBlock(first, speedSlot, accelWord="Acceleration"):
    names = ["Low Slow", "Low Fast", "Low Accel", "Low Level", "High Slow", "High Fast", "High Accel", "High Level"]
    kinds = ["rotSlow", "rotFast", "rotAccel", "rotLevel"] * 2
    rows = [P(first + i, kinds[i], names[i]) for i in range(8)]
    rows.append(P(first + 8, "separation"))
    rows.append(P(speedSlot, "speed"))
    return rows


def phaserBlock(first, rate="rate1", mixName="Phaser Mix"):
    return [
        P(first, "manual", "Phaser Manual"),
        P(first + 1, rate, "Phaser Rate"),
        P(first + 2, "depth", "Phaser Depth"),
        P(first + 3, "depth", "Phaser Resonance"),
        P(first + 4, "depth", mixName),
    ]


def wahBlock(first):
    return [
        P(first, "filter2", "Wah Filter Type"),
        P(first + 1, "depth", "Wah Sensitivity"),
        P(first + 2, "manual", "Wah Manual"),
        P(first + 3, "depth", "Wah Peak"),
        P(first + 4, "rate1", "Wah Rate"),
        P(first + 5, "depth", "Wah Depth"),
        P(first + 6, "plain", "Wah Polarity", table="gsPolarity"),
    ]


def compBlock():
    return [
        P(1, "compSustain"),
        P(2, "compAttack"),
        P(3, "compLevel"),
        P(4, "compSwitch"),
    ]


def midEq(first):
    return [P(first, "eqFreq"), P(first + 1, "eqQ"), P(first + 2, "eqGain")]


def modulationBlock(first, rate="rate2"):
    return [
        P(first, "modType"),
        P(first + 1, rate),
        P(first + 2, "depth"),
        P(first + 3, "feedback", "Flanger Feedback"),
        P(first + 4, "plain", "Chorus Level"),
    ]


TYPES = {
    "Thru": [],
    "Equalizer": [
        P(1, "plain", "Low Frequency", table="gsEqLowFreq"),
        P(2, "lowGain"),
        P(3, "plain", "High Frequency", table="gsEqHighFreq"),
        P(4, "highGain"),
        P(5, "eqFreq", "Mid 1 Frequency"),
        P(6, "eqQ", "Mid 1 Q"),
        P(7, "eqGain", "Mid 1 Gain"),
        P(8, "eqFreq", "Mid 2 Frequency"),
        P(9, "eqQ", "Mid 2 Q"),
        P(10, "eqGain", "Mid 2 Gain"),
        P(20, "level"),
    ],
    "Spectrum": [
        P(1, "eqGain", "250 Hz Gain"),
        P(2, "eqGain", "500 Hz Gain"),
        P(3, "eqGain", "1 kHz Gain"),
        P(4, "eqGain", "1.25 kHz Gain"),
        P(5, "eqGain", "2 kHz Gain"),
        P(6, "eqGain", "3.15 kHz Gain"),
        P(7, "eqGain", "4 kHz Gain"),
        P(8, "eqGain", "8 kHz Gain"),
        P(9, "eqQ", "Band Q"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "Enhancer": [
        P(1, "plain", "Sensitivity"),
        P(2, "plain", "Mix Level"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(20, "level"),
    ],
    "Humanizer": [
        P(1, "drive"),
        P(2, "driveSwitch"),
        P(3, "plain", "Vowel", table="gsVowel"),
        P(4, "plain", "Accel", memo="How fast the vowel changes."),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "Overdrive": [
        P(1, "drive"),
        P(2, "amp"),
        P(3, "ampSwitch"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "Distortion": [
        P(1, "drive"),
        P(2, "amp"),
        P(3, "ampSwitch"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "Tremolo": [
        P(1, "wave"),
        P(2, "rate1"),
        P(3, "depth"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(20, "level"),
    ],
    "Auto Pan": [
        P(1, "wave"),
        P(2, "rate1"),
        P(3, "depth"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(20, "level"),
    ],
    "Compressor": [
        P(1, "plain", "Sustain", memo="How fast the gain comes back."),
        P(2, "plain", "Attack"),
        P(3, "plain", "Post Gain", table="gsPostGain"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "Limiter": [
        P(1, "plain", "Threshold"),
        P(2, "plain", "Ratio", table="gsLimiterRatio"),
        P(3, "plain", "Release"),
        P(4, "plain", "Post Gain", table="gsPostGain"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "St. Chorus": [
        P(1, "filter3"),
        P(2, "cutoff", "Filter Cutoff"),
        P(3, "preDelay"),
        P(4, "rate1"),
        P(5, "depth"),
        P(7, "phase"),
    ]
    + common(),
    "St. Flanger": [
        P(1, "filter3"),
        P(2, "cutoff", "Filter Cutoff"),
        P(3, "preDelay"),
        P(4, "rate1"),
        P(5, "depth"),
        P(6, "feedback"),
        P(7, "phase"),
    ]
    + common(),
    "Step Flanger": [
        P(1, "preDelay"),
        P(2, "rate1"),
        P(3, "depth"),
        P(4, "feedback"),
        P(5, "phase"),
        P(6, "rate1", "Step Rate"),
    ]
    + common(),
    "Space D": [
        P(1, "preDelay"),
        P(2, "rate1"),
        P(3, "depth"),
        P(4, "phase"),
    ]
    + common(),
    "Hexa Chorus": [
        P(1, "preDelay"),
        P(2, "rate1"),
        P(3, "depth"),
        P(4, "plain", "Pre Delay Deviation", memo="0 to 20 ms spread over the six taps."),
        P(5, "plain", "Depth Deviation", table="gsSigned"),
        P(6, "plain", "Pan Deviation", memo="0 to 20."),
    ]
    + common(),
    "Tremolo Chorus": [
        P(1, "preDelay"),
        P(2, "rate1", "Chorus Rate"),
        P(3, "depth", "Chorus Depth"),
        P(4, "phase", "Tremolo Phase"),
        P(5, "rate1", "Tremolo Rate"),
        P(6, "depth", "Tremolo Depth"),
    ]
    + common(),
    "Stereo Delay": [
        P(1, "delay3", "Delay Left"),
        P(2, "delay3", "Delay Right"),
        P(3, "feedback"),
        P(4, "plain", "Feedback Mode", table="gsFbMode"),
        P(5, "plain", "Phase Left", table="gsPhaseInv"),
        P(6, "plain", "Phase Right", table="gsPhaseInv"),
        P(8, "hfDamp"),
    ]
    + common(),
    "Mod Delay": [
        P(1, "delay3", "Delay Left"),
        P(2, "delay3", "Delay Right"),
        P(3, "feedback"),
        P(4, "plain", "Feedback Mode", table="gsFbMode"),
        P(5, "rate1"),
        P(6, "depth"),
        P(7, "phase"),
        P(8, "hfDamp"),
    ]
    + common(),
    "Triple Tap": [
        P(1, "delay1", "Delay Center"),
        P(2, "delay1", "Delay Left"),
        P(3, "delay1", "Delay Right"),
        P(4, "feedback"),
        P(5, "plain", "Level Center"),
        P(6, "plain", "Level Left"),
        P(7, "plain", "Level Right"),
        P(8, "hfDamp"),
    ]
    + common(),
    "Quad Tap": [
        P(1, "delay1", "Delay 1"),
        P(2, "delay1", "Delay 2"),
        P(3, "delay1", "Delay 3"),
        P(4, "delay1", "Delay 4"),
        P(5, "plain", "Level 1"),
        P(6, "plain", "Level 2"),
        P(7, "plain", "Level 3"),
        P(8, "plain", "Level 4"),
        P(9, "feedback"),
        P(10, "hfDamp"),
    ]
    + common(),
    "Time Ctrl Delay": [
        P(1, "delay2"),
        P(2, "plain", "Acceleration", table="gsAccel", memo="Slew speed of the delay time. Changing the time bends the pitch."),
        P(3, "feedback"),
        P(4, "hfDamp"),
        P(5, "pan"),
    ]
    + common(),
    "2Voice Pitch Shifter": [
        P(1, "coarse", "Coarse A"),
        P(2, "fine", "Fine A"),
        P(3, "preDelay", "Pre Delay A"),
        P(4, "pan", "Pan A"),
        P(5, "coarse", "Coarse B"),
        P(6, "fine", "Fine B"),
        P(7, "preDelay", "Pre Delay B"),
        P(8, "pan", "Pan B"),
        P(9, "pitchMode"),
        P(10, "plain", "Level Balance A/B", memo="0 is voice A only, 127 is voice B only."),
    ]
    + common(),
    "Fb P.Shifter": [
        P(1, "coarse"),
        P(2, "fine"),
        P(3, "feedback"),
        P(4, "preDelay"),
        P(5, "pitchMode"),
        P(6, "pan"),
    ]
    + common(),
    "Phaser": phaserBlock(1, "rate1", "Mix")
    + [P(17, "lowGain"), P(18, "highGain"), P(20, "level")],
    "Auto Wah": [
        P(1, "filter2"),
        P(2, "depth", "Sensitivity"),
        P(3, "manual"),
        P(4, "depth", "Peak"),
        P(5, "rate1"),
        P(6, "depth"),
        P(7, "plain", "Polarity", table="gsPolarity"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "Rotary": [
        P(1, "rotSlow", "Low Slow"),
        P(2, "rotFast", "Low Fast"),
        P(3, "rotAccel", "Low Accel"),
        P(4, "rotLevel", "Low Level"),
        P(5, "rotSlow", "High Slow"),
        P(6, "rotFast", "High Fast"),
        P(7, "rotAccel", "High Accel"),
        P(8, "rotLevel", "High Level"),
        P(9, "separation"),
        P(11, "speed"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(20, "level"),
    ],
    "Reverb": [
        P(1, "plain", "Reverb Type", table="gsReverbType"),
        P(2, "preDelay"),
        P(3, "plain", "Reverb Time"),
        P(4, "hfDamp"),
    ]
    + common(),
    "Gate Reverb": [
        P(1, "plain", "Gate Type", table="gsGateType"),
        P(2, "preDelay"),
        P(3, "plain", "Gate Time", table="gsGateTime"),
    ]
    + common(),
    "Lo-Fi 1": [
        P(1, "plain", "Pre Filter", table="gsOneBased", memo="1 is dry, 2 to 6 add the compressor."),
        P(2, "plain", "Lo-Fi Type", table="gsOneBased"),
        P(3, "plain", "Post Filter", table="gsOneBased"),
        P(16, "balance"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "Lo-Fi 2": [
        P(1, "plain", "Lo-Fi Type", table="gsOneBased"),
        P(2, "filter3"),
        P(3, "cutoff", "Filter Cutoff"),
        P(4, "plain", "Radio Detune"),
        P(5, "plain", "Radio Noise Level"),
        P(6, "plain", "Noise Type", table="gsNoise"),
        P(7, "plain", "Noise Low Pass", table="gsLpf"),
        P(8, "plain", "Noise Level"),
        P(9, "plain", "Disc Type", table="gsDisc"),
        P(10, "plain", "Disc Low Pass", table="gsLpf"),
        P(11, "plain", "Disc Level"),
        P(12, "plain", "Hum Type", table="gsHum"),
        P(13, "plain", "Hum Low Pass", table="gsLpf"),
        P(14, "plain", "Hum Level"),
        P(15, "monoStereo"),
        P(16, "balance"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan", memo="Mono only."),
        P(20, "level"),
    ],
    "3D Auto": [
        P(1, "azimuth", "Stop Azimuth"),
        P(2, "rate1", "Speed"),
        P(3, "plain", "Direction", table="gsCwDirection"),
        P(4, "plain", "Turn", table="gsOnOff"),
        P(15, "output"),
        P(20, "level"),
    ],
    "3D Manual": [
        P(1, "azimuth"),
        P(15, "output"),
        P(20, "level"),
    ],
    "3D Chorus": [
        P(1, "preDelay"),
        P(2, "rate1"),
        P(3, "depth"),
        P(15, "output"),
    ]
    + common(),
    "3D Delay": [
        P(1, "delay3", "Delay Center"),
        P(2, "delay3", "Delay Left"),
        P(3, "delay3", "Delay Right"),
        P(4, "feedback", "Feedback", memo="Feeds back from the center tap. 64 is no feedback."),
        P(5, "plain", "Level Center"),
        P(6, "plain", "Level Left"),
        P(7, "plain", "Level Right"),
        P(8, "hfDamp"),
        P(15, "output"),
    ]
    + common(),
    # Series combinations
    "Chorus -> Delay": twoStage(chorusStage(1), delayStage(6, 10)),
    "Flanger -> Delay": twoStage(flangerStage(1), delayStage(6, 10)),
    "Chorus -> Flanger": twoStage(chorusStage(1), flangerSecond()),
    # Parallel combinations
    "Chorus / Delay": chorusStage(1)
    + delayStage(6, 10)
    + parallelPans("Chorus", "Delay"),
    "Flanger / Delay": flangerStage(1)
    + delayStage(6, 10)
    + parallelPans("Flanger", "Delay"),
    "Chorus / Flanger": chorusStage(1)
    + flangerSecond()
    + parallelPans("Chorus", "Flanger"),
    "OD1 / OD2": odBlock(0, "OD1 ")
    + odBlock(5, "OD2 ")
    + parallelPans("OD1", "OD2"),
    "OD / Rotary": odBlock(0, "OD ")
    + rotaryBlock(6, 15)
    + parallelPans("Drive", "Rotary"),
    "OD / Phaser": odBlock(0, "OD ")
    + phaserBlock(6, "rate1", "Phaser Mix")
    + parallelPans("Drive", "Phaser"),
    "OD / AutoWah": odBlock(0, "OD ")
    + wahBlock(6)
    + parallelPans("Drive", "Wah"),
    "PH / Rotary": phaserBlock(1, "rate1", "Phaser Mix")
    + rotaryBlock(6, 15)
    + parallelPans("Phaser", "Rotary"),
    "PH / AutoWah": phaserBlock(1, "rate1", "Phaser Mix")
    + wahBlock(6)
    + parallelPans("Phaser", "Wah"),
    # Overdrive / Distortion -> modulation / delay
    "Overdrive -> Chorus": driveBlock() + driveTail(chorusSecond()),
    "Overdrive -> Flanger": driveBlock() + driveTail(flangerSecond()),
    "Overdrive -> Delay": driveBlock() + driveTail(delayStage(6, 10)),
    "Distortion -> Chorus": driveBlock() + driveTail(chorusSecond()),
    "Distortion -> Flanger": driveBlock() + driveTail(flangerSecond()),
    "Distortion -> Delay": driveBlock() + driveTail(delayStage(6, 10)),
    "Enhancer -> Chorus": enhancerBlock() + driveTail(chorusSecond()),
    "Enhancer -> Flanger": enhancerBlock() + driveTail(flangerSecond()),
    "Enhancer -> Delay": enhancerBlock() + driveTail(delayStage(6, 10)),
    # Multi effects
    "Rhodes Multi": [
        P(1, "plain", "Enhancer Sensitivity"),
        P(2, "plain", "Enhancer Mix Level"),
        P(3, "manual", "Phaser Manual"),
        P(4, "rate2", "Phaser Rate"),
        P(5, "depth", "Phaser Depth"),
        P(6, "depth", "Phaser Resonance"),
        P(7, "depth", "Phaser Mix"),
        P(8, "modType"),
        P(9, "cutoff", "Chorus Low Pass", memo="120 and above is off."),
        P(10, "preDelay", "Chorus Pre Delay"),
        P(11, "rate2", "Chorus Rate"),
        P(12, "depth", "Chorus Depth"),
        P(13, "feedback", "Flanger Feedback"),
        P(14, "plain", "Chorus Level"),
        P(15, "plain", "Tremolo / Auto Pan", table="gsTremoloType"),
        P(16, "wave", "Tremolo Wave"),
        P(17, "rate2", "Tremolo Rate"),
        P(18, "depth", "Tremolo Depth"),
        P(19, "plain", "Tremolo Switch", table="gsOnOff"),
        P(20, "level"),
    ],
    "Keyboard Multi": [
        P(1, "plain", "Ring Mod Frequency", memo="One semitone per step, 69 is 440 Hz."),
        P(2, "plain", "Ring Mod Balance"),
        P(3, "lowGain"),
    ]
    + midEq(4)
    + [
        P(7, "highGain"),
        P(8, "coarse"),
        P(9, "fine"),
        P(10, "pitchMode"),
        P(11, "plain", "Pitch Balance"),
        P(12, "manual", "Phaser Manual"),
        P(13, "rate2", "Phaser Rate"),
        P(14, "depth", "Phaser Depth"),
        P(15, "depth", "Phaser Resonance"),
        P(16, "depth", "Phaser Mix"),
        P(17, "delay4"),
        P(18, "feedback"),
        P(19, "plain", "Delay Level"),
        P(20, "level"),
    ],
    "Rotary Multi": [
        P(1, "drive"),
        P(2, "driveSwitch"),
        P(3, "lowGain"),
    ]
    + midEq(4)
    + [P(7, "highGain")]
    + rotaryBlock(8, 17)
    + [P(20, "level")],
    "GTR Multi 1": compBlock()
    + [
        P(5, "driveType"),
        P(6, "drive"),
        P(7, "amp"),
        P(8, "ampSwitch"),
        P(9, "lowGain"),
        P(10, "highGain"),
        P(11, "driveSwitch"),
    ]
    + modulationBlock(12)
    + [
        P(17, "delay4"),
        P(18, "feedback"),
        P(19, "plain", "Delay Level"),
        P(20, "level"),
    ],
    "GTR Multi 2": compBlock()
    + [
        P(5, "driveType"),
        P(6, "drive"),
        P(7, "amp"),
        P(8, "ampSwitch"),
        P(9, "driveSwitch"),
        P(10, "lowGain"),
    ]
    + midEq(11)
    + [P(14, "highGain")]
    + modulationBlock(15)
    + [P(20, "level")],
    "GTR Multi 3": [
        P(1, "filter2", "Wah Filter Type"),
        P(2, "manual", "Wah Manual"),
        P(3, "depth", "Wah Peak"),
        P(4, "plain", "Wah Switch", table="gsOnOff"),
        P(5, "driveType"),
        P(6, "drive"),
        P(7, "amp"),
        P(8, "ampSwitch"),
        P(9, "lowGain"),
        P(10, "highGain"),
        P(11, "driveSwitch"),
    ]
    + modulationBlock(12)
    + [
        P(17, "delay4"),
        P(18, "feedback"),
        P(19, "plain", "Delay Level"),
        P(20, "level"),
    ],
    "Clean GTR Multi 1": compBlock()
    + [P(5, "lowGain")]
    + midEq(6)
    + [P(9, "highGain")]
    + modulationBlock(10)
    + [
        P(15, "delay4"),
        P(16, "feedback"),
        P(17, "hfDamp"),
        P(18, "plain", "Delay Level"),
        P(20, "level"),
    ],
    "Clean GTR Multi 2": [
        P(1, "filter2", "Wah Filter Type"),
        P(2, "manual", "Wah Manual"),
        P(3, "depth", "Wah Peak"),
        P(4, "rate1", "Wah Rate"),
        P(5, "depth", "Wah Depth"),
        P(6, "plain", "Wah Switch", table="gsOnOff"),
        P(7, "lowGain"),
    ]
    + midEq(8)
    + [P(11, "highGain")]
    + modulationBlock(12)
    + [
        P(17, "delay4"),
        P(18, "feedback"),
        P(19, "plain", "Delay Level"),
        P(20, "level"),
    ],
    "Bass Multi": compBlock()
    + [
        P(5, "driveType"),
        P(6, "drive"),
        P(7, "plain", "Amp Type", memo="0 to 2."),
        P(8, "ampSwitch"),
        P(9, "driveSwitch"),
        P(10, "lowGain"),
    ]
    + midEq(11)
    + [P(14, "highGain")]
    + modulationBlock(15)
    + [P(20, "level")],
}

# What EFX control source 1 and 2 move for each type (the synth's own
# comments, which follow the manual). Used for the generated reference.
CONTROLS = {
    "Thru": ("-", "-"),
    "Equalizer": ("Level", "-"),
    "Spectrum": ("Pan", "Level"),
    "Enhancer": ("Sensitivity", "Mix Level"),
    "Humanizer": ("Vowel (up to 4 vowels either way)", "Level"),
    "Overdrive": ("Drive", "Pan"),
    "Distortion": ("Drive", "Pan"),
    "Tremolo": ("Rate", "Depth"),
    "Auto Pan": ("Rate", "Depth"),
    "Compressor": ("Pan", "Level"),
    "Limiter": ("Pan", "Level"),
    "St. Chorus": ("Rate", "Effect Balance"),
    "St. Flanger": ("Rate", "Feedback"),
    "Step Flanger": ("Feedback", "Step Rate"),
    "Space D": ("Rate", "Effect Balance"),
    "Hexa Chorus": ("Rate", "Effect Balance"),
    "Tremolo Chorus": ("Tremolo Rate", "Effect Balance"),
    "Stereo Delay": ("Feedback", "Effect Balance"),
    "Mod Delay": ("Rate", "Effect Balance"),
    "Triple Tap": ("Feedback", "Effect Balance"),
    "Quad Tap": ("Feedback", "Effect Balance"),
    "Time Ctrl Delay": ("Delay Time", "Feedback"),
    "2Voice Pitch Shifter": ("Pitch Coarse A", "Pitch Coarse B"),
    "Fb P.Shifter": ("Pitch Coarse", "Feedback"),
    "Phaser": ("Manual", "Rate"),
    "Auto Wah": ("Manual", "Rate"),
    "Rotary": ("Speed", "Level"),
    "Reverb": ("Reverb Time", "Effect Balance"),
    "Gate Reverb": ("Effect Balance", "Level"),
    "Lo-Fi 1": ("Effect Balance", "Pan"),
    "Lo-Fi 2": ("Radio Detune", "Effect Balance"),
    "3D Auto": ("Speed", "Turn (steps of 64)"),
    "3D Manual": ("Azimuth", "Level"),
    "3D Chorus": ("Rate", "Effect Balance"),
    "3D Delay": ("Feedback", "Effect Balance"),
    "Chorus -> Delay": ("Chorus Balance", "Delay Balance"),
    "Flanger -> Delay": ("Flanger Feedback", "Delay Balance"),
    "Chorus -> Flanger": ("Chorus Balance", "Flanger Balance"),
    "Chorus / Delay": ("Chorus Balance", "Delay Balance"),
    "Flanger / Delay": ("Flanger Balance", "Delay Balance"),
    "Chorus / Flanger": ("Chorus Balance", "Flanger Balance"),
    "OD1 / OD2": ("OD1 Drive", "OD2 Drive"),
    "OD / Rotary": ("Drive", "Speed"),
    "OD / Phaser": ("Drive", "Phaser Rate"),
    "OD / AutoWah": ("Drive", "Wah Manual"),
    "PH / Rotary": ("Phaser Rate", "Speed"),
    "PH / AutoWah": ("Phaser Rate", "Wah Manual"),
    "Overdrive -> Chorus": ("Drive Pan", "Chorus Balance"),
    "Overdrive -> Flanger": ("Drive Pan", "Flanger Balance"),
    "Overdrive -> Delay": ("Drive Pan", "Delay Balance"),
    "Distortion -> Chorus": ("Drive Pan", "Chorus Balance"),
    "Distortion -> Flanger": ("Drive Pan", "Flanger Balance"),
    "Distortion -> Delay": ("Drive Pan", "Delay Balance"),
    "Enhancer -> Chorus": ("Enhancer Sensitivity", "Chorus Balance"),
    "Enhancer -> Flanger": ("Enhancer Sensitivity", "Flanger Balance"),
    "Enhancer -> Delay": ("Enhancer Sensitivity", "Delay Balance"),
    "Rhodes Multi": ("Tremolo Rate", "Tremolo Depth"),
    "Keyboard Multi": ("Ring Mod Frequency", "Ring Mod Balance"),
    "Rotary Multi": ("Drive", "Speed"),
    "GTR Multi 1": ("Drive", "Delay Level"),
    "GTR Multi 2": ("Drive", "Chorus Level"),
    "GTR Multi 3": ("Wah Manual", "Drive"),
    "Clean GTR Multi 1": ("Chorus Level", "Delay Level"),
    "Clean GTR Multi 2": ("Wah Manual", "Delay Level"),
    "Bass Multi": ("Drive", "Chorus Level"),
}

# Folders that group the 65 types, in the manual's order.
