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


# Kinds: key -> (table key, memo)

def K(table=None, memo=None):
    return (table, memo)


KINDS = {
    "level": K(None, "Output level of the effect."),
    "plain": K(),
    "pan": K("gsPan"),
    "balance": K(None, "0 is dry only, 127 is effect only."),
    "lowGain": K("gsGain", "Low shelf gain. 64 is flat."),
    "highGain": K("gsGain", "High shelf gain. 64 is flat."),
    "preDelay": K("gsPreDelay"),
    "rate1": K("gsRate1"),
    "rate2": K("gsRate2"),
    "depth": K(),
    "feedback": K("gsFeedback", "64 is no feedback."),
    "hfDamp": K("gsHfDamp", "Lowers the repeats' high end. 120 and above is bypass."),
    "delay1": K("gsDelay1"),
    "delay2": K("gsDelay2"),
    "delay3": K("gsDelay3"),
    "delay4": K("gsDelay4"),
    "phase": K("gsPhase"),
    "wave": K("gsWave"),
    "amp": K("gsAmp"),
    "ampSwitch": K("gsOnOff"),
    "driveType": K("gsDriveType"),
    "drive": K(),
    "driveSwitch": K("gsOnOff"),
    "eqFreq": K("gsEqFreq"),
    "eqQ": K("gsEqQ"),
    "eqGain": K("gsGain"),
    "modType": K("gsModType"),
    "output": K("gsOutput"),
    "monoStereo": K("gsMonoStereo"),
    "coarse": K("gsPitchCoarse"),
    "fine": K("gsPitchFine"),
    "pitchMode": K("gsPitchMode", "Larger modes use a shorter window."),
    "cutoff": K("gsCutoff"),
    "manual": K("gsManual"),
    "filter3": K("gsFilter3"),
    "filter2": K("gsFilter2"),
    "compSustain": K(),
    "compAttack": K(),
    "compLevel": K(),
    "compSwitch": K("gsOnOff"),
    "rotSlow": K("gsRate1"),
    "rotFast": K("gsRate1"),
    "rotAccel": K(),
    "rotLevel": K(),
    "separation": K(),
    "speed": K("gsSpeed", "0-63 slow, 64-127 fast."),
    "azimuth": K("gsAzimuth"),
}


def P(slot, kind, table=None, memo=None):
    """One parameter: slot (1 based), kind key, optional overrides."""
    base = KINDS[kind] if isinstance(kind, str) else kind
    return (
        slot,
        table if table is not None else base[0],
        memo if memo is not None else base[1],
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


def twoStage(first, second, gains=True):
    """Series combinations: first stage 1-5, second stage 6-10."""
    rows = list(first) + list(second)
    if gains:
        rows += [P(17, "lowGain"), P(18, "highGain")]
    rows.append(P(20, "level"))
    return rows


def chorusStage(base=1):
    return [
        P(base, "preDelay"),
        P(base + 1, "rate1"),
        P(base + 2, "depth"),
        P(base + 4, "balance"),
    ]


def flangerStage(base=1):
    return [
        P(base, "preDelay"),
        P(base + 1, "rate1"),
        P(base + 2, "depth"),
        P(base + 3, "feedback"),
        P(base + 4, "balance"),
    ]


def delayStage(base=6, balanceSlot=10):
    return [
        P(base, "delay3"),
        P(base + 1, "feedback"),
        P(base + 2, "hfDamp"),
        P(balanceSlot, "balance"),
    ]


def chorusSecond():
    return [
        P(6, "preDelay"),
        P(7, "rate1"),
        P(8, "depth"),
        P(10, "balance"),
    ]


def flangerSecond():
    return [
        P(6, "preDelay"),
        P(7, "rate1"),
        P(8, "depth"),
        P(9, "feedback"),
        P(10, "balance"),
    ]


def driveBlock():
    """OD / DS -> X: slots 1-4 (drive, drive pan, amp type, amp switch)."""
    return [
        P(1, "drive"),
        P(2, "pan"),
        P(3, "amp"),
        P(4, "ampSwitch"),
    ]


def enhancerBlock():
    return [
        P(1, "plain", memo="How strongly high frequencies are enhanced."),
        P(2, "plain"),
    ]


def driveTail(second):
    return list(second) + [P(17, "lowGain"), P(18, "highGain"), P(20, "level")]


def parallelPans():
    return [
        P(16, "pan"),
        P(17, "plain"),
        P(18, "pan"),
        P(19, "plain"),
        P(20, "level"),
    ]


def odBlock(offset=0):
    return [
        P(1 + offset, "driveType"),
        P(2 + offset, "drive"),
        P(3 + offset, "amp"),
        P(4 + offset, "ampSwitch"),
    ]


def rotaryBlock(first, speedSlot):
    kinds = ["rotSlow", "rotFast", "rotAccel", "rotLevel"] * 2
    rows = [P(first + i, kinds[i]) for i in range(8)]
    rows.append(P(first + 8, "separation"))
    rows.append(P(speedSlot, "speed"))
    return rows


def phaserBlock(first, rate="rate1"):
    return [
        P(first, "manual"),
        P(first + 1, rate),
        P(first + 2, "depth"),
        P(first + 3, "depth"),
        P(first + 4, "depth"),
    ]


def wahBlock(first):
    return [
        P(first, "filter2"),
        P(first + 1, "depth"),
        P(first + 2, "manual"),
        P(first + 3, "depth"),
        P(first + 4, "rate1"),
        P(first + 5, "depth"),
        P(first + 6, "plain", table="gsPolarity"),
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
        P(first + 3, "feedback"),
        P(first + 4, "plain"),
    ]


TYPES = {
    "Thru": [],
    "Equalizer": [
        P(1, "plain", table="gsEqLowFreq"),
        P(2, "lowGain"),
        P(3, "plain", table="gsEqHighFreq"),
        P(4, "highGain"),
        P(5, "eqFreq"),
        P(6, "eqQ"),
        P(7, "eqGain"),
        P(8, "eqFreq"),
        P(9, "eqQ"),
        P(10, "eqGain"),
        P(20, "level"),
    ],
    "Spectrum": [
        P(1, "eqGain"),
        P(2, "eqGain"),
        P(3, "eqGain"),
        P(4, "eqGain"),
        P(5, "eqGain"),
        P(6, "eqGain"),
        P(7, "eqGain"),
        P(8, "eqGain"),
        P(9, "eqQ"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "Enhancer": [
        P(1, "plain"),
        P(2, "plain"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(20, "level"),
    ],
    "Humanizer": [
        P(1, "drive"),
        P(2, "driveSwitch"),
        P(3, "plain", table="gsVowel"),
        P(4, "plain", memo="How fast the vowel changes."),
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
        P(1, "plain", memo="How fast the gain comes back."),
        P(2, "plain"),
        P(3, "plain", table="gsPostGain"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "Limiter": [
        P(1, "plain"),
        P(2, "plain", table="gsLimiterRatio"),
        P(3, "plain"),
        P(4, "plain", table="gsPostGain"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "St. Chorus": [
        P(1, "filter3"),
        P(2, "cutoff"),
        P(3, "preDelay"),
        P(4, "rate1"),
        P(5, "depth"),
        P(7, "phase"),
    ]
    + common(),
    "St. Flanger": [
        P(1, "filter3"),
        P(2, "cutoff"),
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
        P(6, "rate1"),
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
        P(4, "plain", memo="0 to 20 ms spread over the six taps."),
        P(5, "plain", table="gsSigned"),
        P(6, "plain", memo="0 to 20."),
    ]
    + common(),
    "Tremolo Chorus": [
        P(1, "preDelay"),
        P(2, "rate1"),
        P(3, "depth"),
        P(4, "phase"),
        P(5, "rate1"),
        P(6, "depth"),
    ]
    + common(),
    "Stereo Delay": [
        P(1, "delay3"),
        P(2, "delay3"),
        P(3, "feedback"),
        P(4, "plain", table="gsFbMode"),
        P(5, "plain", table="gsPhaseInv"),
        P(6, "plain", table="gsPhaseInv"),
        P(8, "hfDamp"),
    ]
    + common(),
    "Mod Delay": [
        P(1, "delay3"),
        P(2, "delay3"),
        P(3, "feedback"),
        P(4, "plain", table="gsFbMode"),
        P(5, "rate1"),
        P(6, "depth"),
        P(7, "phase"),
        P(8, "hfDamp"),
    ]
    + common(),
    "Triple Tap": [
        P(1, "delay1"),
        P(2, "delay1"),
        P(3, "delay1"),
        P(4, "feedback"),
        P(5, "plain"),
        P(6, "plain"),
        P(7, "plain"),
        P(8, "hfDamp"),
    ]
    + common(),
    "Quad Tap": [
        P(1, "delay1"),
        P(2, "delay1"),
        P(3, "delay1"),
        P(4, "delay1"),
        P(5, "plain"),
        P(6, "plain"),
        P(7, "plain"),
        P(8, "plain"),
        P(9, "feedback"),
        P(10, "hfDamp"),
    ]
    + common(),
    "Time Ctrl Delay": [
        P(1, "delay2"),
        P(2, "plain", table="gsAccel", memo="Slew speed of the delay time. Changing the time bends the pitch."),
        P(3, "feedback"),
        P(4, "hfDamp"),
        P(5, "pan"),
    ]
    + common(),
    "2Voice Pitch Shifter": [
        P(1, "coarse"),
        P(2, "fine"),
        P(3, "preDelay"),
        P(4, "pan"),
        P(5, "coarse"),
        P(6, "fine"),
        P(7, "preDelay"),
        P(8, "pan"),
        P(9, "pitchMode"),
        P(10, "plain", memo="0 is voice A only, 127 is voice B only."),
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
    "Phaser": phaserBlock(1, "rate1")
    + [P(17, "lowGain"), P(18, "highGain"), P(20, "level")],
    "Auto Wah": [
        P(1, "filter2"),
        P(2, "depth"),
        P(3, "manual"),
        P(4, "depth"),
        P(5, "rate1"),
        P(6, "depth"),
        P(7, "plain", table="gsPolarity"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "Rotary": [
        P(1, "rotSlow"),
        P(2, "rotFast"),
        P(3, "rotAccel"),
        P(4, "rotLevel"),
        P(5, "rotSlow"),
        P(6, "rotFast"),
        P(7, "rotAccel"),
        P(8, "rotLevel"),
        P(9, "separation"),
        P(11, "speed"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(20, "level"),
    ],
    "Reverb": [
        P(1, "plain", table="gsReverbType"),
        P(2, "preDelay"),
        P(3, "plain"),
        P(4, "hfDamp"),
    ]
    + common(),
    "Gate Reverb": [
        P(1, "plain", table="gsGateType"),
        P(2, "preDelay"),
        P(3, "plain", table="gsGateTime"),
    ]
    + common(),
    "Lo-Fi 1": [
        P(1, "plain", table="gsOneBased", memo="1 is dry, 2 to 6 add the compressor."),
        P(2, "plain", table="gsOneBased"),
        P(3, "plain", table="gsOneBased"),
        P(16, "balance"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan"),
        P(20, "level"),
    ],
    "Lo-Fi 2": [
        P(1, "plain", table="gsOneBased"),
        P(2, "filter3"),
        P(3, "cutoff"),
        P(4, "plain"),
        P(5, "plain"),
        P(6, "plain", table="gsNoise"),
        P(7, "plain", table="gsLpf"),
        P(8, "plain"),
        P(9, "plain", table="gsDisc"),
        P(10, "plain", table="gsLpf"),
        P(11, "plain"),
        P(12, "plain", table="gsHum"),
        P(13, "plain", table="gsLpf"),
        P(14, "plain"),
        P(15, "monoStereo"),
        P(16, "balance"),
        P(17, "lowGain"),
        P(18, "highGain"),
        P(19, "pan", memo="Mono only."),
        P(20, "level"),
    ],
    "3D Auto": [
        P(1, "azimuth"),
        P(2, "rate1"),
        P(3, "plain", table="gsCwDirection"),
        P(4, "plain", table="gsOnOff"),
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
        P(1, "delay3"),
        P(2, "delay3"),
        P(3, "delay3"),
        P(4, "feedback", memo="Feeds back from the center tap. 64 is no feedback."),
        P(5, "plain"),
        P(6, "plain"),
        P(7, "plain"),
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
    + parallelPans(),
    "Flanger / Delay": flangerStage(1)
    + delayStage(6, 10)
    + parallelPans(),
    "Chorus / Flanger": chorusStage(1)
    + flangerSecond()
    + parallelPans(),
    "OD1 / OD2": odBlock(0)
    + odBlock(5)
    + parallelPans(),
    "OD / Rotary": odBlock(0)
    + rotaryBlock(6, 15)
    + parallelPans(),
    "OD / Phaser": odBlock(0)
    + phaserBlock(6, "rate1")
    + parallelPans(),
    "OD / AutoWah": odBlock(0)
    + wahBlock(6)
    + parallelPans(),
    "PH / Rotary": phaserBlock(1, "rate1")
    + rotaryBlock(6, 15)
    + parallelPans(),
    "PH / AutoWah": phaserBlock(1, "rate1")
    + wahBlock(6)
    + parallelPans(),
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
        P(1, "plain"),
        P(2, "plain"),
        P(3, "manual"),
        P(4, "rate2"),
        P(5, "depth"),
        P(6, "depth"),
        P(7, "depth"),
        P(8, "modType"),
        P(9, "cutoff", memo="120 and above is off."),
        P(10, "preDelay"),
        P(11, "rate2"),
        P(12, "depth"),
        P(13, "feedback"),
        P(14, "plain"),
        P(15, "plain", table="gsTremoloType"),
        P(16, "wave"),
        P(17, "rate2"),
        P(18, "depth"),
        P(19, "plain", table="gsOnOff"),
        P(20, "level"),
    ],
    "Keyboard Multi": [
        P(1, "plain", memo="One semitone per step, 69 is 440 Hz."),
        P(2, "plain"),
        P(3, "lowGain"),
    ]
    + midEq(4)
    + [
        P(7, "highGain"),
        P(8, "coarse"),
        P(9, "fine"),
        P(10, "pitchMode"),
        P(11, "plain"),
        P(12, "manual"),
        P(13, "rate2"),
        P(14, "depth"),
        P(15, "depth"),
        P(16, "depth"),
        P(17, "delay4"),
        P(18, "feedback"),
        P(19, "plain"),
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
        P(19, "plain"),
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
        P(1, "filter2"),
        P(2, "manual"),
        P(3, "depth"),
        P(4, "plain", table="gsOnOff"),
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
        P(19, "plain"),
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
        P(18, "plain"),
        P(20, "level"),
    ],
    "Clean GTR Multi 2": [
        P(1, "filter2"),
        P(2, "manual"),
        P(3, "depth"),
        P(4, "rate1"),
        P(5, "depth"),
        P(6, "plain", table="gsOnOff"),
        P(7, "lowGain"),
    ]
    + midEq(8)
    + [P(11, "highGain")]
    + modulationBlock(12)
    + [
        P(17, "delay4"),
        P(18, "feedback"),
        P(19, "plain"),
        P(20, "level"),
    ],
    "Bass Multi": compBlock()
    + [
        P(5, "driveType"),
        P(6, "drive"),
        P(7, "plain", memo="0 to 2."),
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
