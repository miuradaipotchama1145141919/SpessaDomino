import os
import yaml

from DominoDefBuilder.loader import readYaml as loadYaml

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataDir = os.path.join(root, "scripts", "data")
moduleDir = os.path.join(root, "modules", "spessasynth")
outDir = os.path.join(root, "build")

gm1Keys = (
    "Acoustic Bass Drum,Bass Drum 1,Side Stick,Acoustic Snare,Hand Clap,Electric Snare,"
    "Low Floor Tom,Closed Hi-Hat,High Floor Tom,Pedal Hi-Hat,Low Tom,Open Hi-Hat,"
    "Low-Mid Tom,Hi-Mid Tom,Crash Cymbal 1,High Tom,Ride Cymbal 1,Chinese Cymbal,"
    "Ride Bell,Tambourine,Splash Cymbal,Cowbell,Crash Cymbal 2,Vibraslap,Ride Cymbal 2,"
    "Hi Bongo,Low Bongo,Mute Hi Conga,Open Hi Conga,Low Conga,High Timbale,Low Timbale,"
    "High Agogo,Low Agogo,Cabasa,Maracas,Short Whistle,Long Whistle,Short Guiro,"
    "Long Guiro,Claves,Hi Wood Block,Low Wood Block,Mute Cuica,Open Cuica,"
    "Mute Triangle,Open Triangle"
).split(",")

gsKits = [
    (1, "Standard 1 (GM1 Standard)"),
    (2, "Standard 2"),
    (9, "Room"),
    (17, "Power"),
    (25, "Electronic"),
    (26, "TR-808"),
    (33, "Jazz"),
    (41, "Brush"),
    (49, "Orchestra"),
    (57, "SFX"),
    (128, "CM-64/CM-32L"),
]

# MU128E2 XG voice and drum definitions transcribed from the manual tables.
# Generated source data lives in scripts/data/mu128XgVoices.yaml and
# scripts/data/mu128XgDrums.yaml so regeneration does not require PDF tooling.
XG_NORMAL_LSB_LABELS = {
    0: "MU Basic",
    1: "Key Scale",
    3: "Panning",
    6: "Stereo",
    8: "Single",
    12: "Fast Decay",
    14: "Double Attack",
    16: "Bright 1",
    17: "Bright 2",
    18: "Dark 1",
    19: "Dark 2",
    20: "Resonant",
    21: "LFO-Cutoff Frequency",
    22: "Velocity-Cutoff Frequency",
    24: "Attack",
    25: "Release",
    26: "Sweep",
    27: "Resonant Sweep",
    37: "5th 1",
    38: "5th 2",
    39: "Bend",
    40: "Tutti 1",
    41: "Tutti 2",
    48: "Other Instrument 1",
    56: "Other Instrument 2",
    64: "Other Waves 1",
    65: "Other Waves 2",
    66: "Other Waves 3",
    67: "Other Waves 4",
    68: "Other Waves 5",
    72: "Other Instrument 3",
    76: "Other Waves 13",
    77: "Other Waves 14",
    78: "Other Waves 15",
    79: "Other Waves 16",
    80: "Other Waves 17",
    88: "Other Waves 25",
    89: "Other Waves 26",
    90: "Other Waves 27",
    91: "Other Waves 28",
    96: "Other Instrument 1",
    98: "Other Instrument 2",
    126: "Capital Voices on MU100 Native Map",
    127: "Capital Voices on MU Basic Map",
}
XG_NORMAL_LSBS = [
    0,
    1,
    3,
    6,
    8,
    12,
    14,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    24,
    25,
    26,
    27,
    28,
    29,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    45,
    48,
    52,
    53,
    54,
    64,
    65,
    66,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    76,
    77,
    78,
    79,
    80,
    81,
    82,
    83,
    84,
    85,
    86,
    87,
    88,
    89,
    90,
    91,
    96,
    97,
    98,
    99,
    100,
    101,
    126,
    127,
]
XG_EXCLUSIVE_LSB_LABELS = {
    0: "Timbre",
    8: "Timbre, Poly",
    16: "Timbre, Looped",
    24: "Timbre, Looped, Poly",
    48: "Phrase, Looped",
    56: "Phrase, Looped, Poly",
    64: "SFX, Timbre",
}


def readPart(name):
    with open(os.path.join(moduleDir, "parts", name), encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def readYaml(name):
    return loadYaml(os.path.join(dataDir, name))


class noAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def writeYaml(name, data):
    os.makedirs(outDir, exist_ok=True)
    with open(os.path.join(outDir, name), "w", encoding="utf-8") as handle:
        yaml.dump(
            data,
            handle,
            Dumper=noAliasDumper,
            sort_keys=False,
            width=200,
            allow_unicode=True,
        )


def gm1Tones():
    return dict((35 + index, name) for index, name in enumerate(gm1Keys))


def gsBanks(name):
    return [
        {"name": "%s (Capital)" % name if msb == 0 else "MSB %03d" % msb, "msb": msb}
        for msb in range(128)
    ]


def xgVariationBanks(pc, voiceData):
    banks = [{"name": "MU Basic", "msb": 0, "lsb": 0}]
    for lsb in XG_NORMAL_LSBS:
        if lsb == 0:
            continue
        patch = voiceData["banks"].get("0:%d" % lsb, {}).get(str(pc))
        if patch:
            banks.append({"name": patch, "msb": 0, "lsb": lsb})
    for lsb in sorted({int(key.split(":")[1]) for key in voiceData["exclusiveBanks"]}):
        patch = voiceData["exclusiveBanks"].get("48:%d" % lsb, {}).get(str(pc))
        if patch:
            banks.append({"name": patch, "msb": 48, "lsb": lsb})
    return banks


def sc8850Data():
    """Load static Sound Canvas maps transcribed from the SC-8850 map source.

    YAML is bundled with the project, so regeneration does not depend on XML
    parsing or on the original SC-8850 editor/source file.
    """
    return readYaml("sc8850Maps.yaml")


def buildScVoices():
    source = sc8850Data()
    return [
        {
            "name": "Sound Canvas %s (MSB/LSB variations)" % sourceMap["name"],
            "programs": [
                {
                    "pc": program["pc"],
                    "name": program["name"],
                    "banks": [
                        dict({"name": bank["name"]}, msb=bank["msb"], lsb=bank["lsb"])
                        for bank in program["banks"]
                    ],
                }
                for program in sourceMap["programs"]
            ],
        }
        for sourceMap in source["instrumentMaps"]
    ]


def buildScDrums(toneSets):
    source = sc8850Data()
    maps = []
    for sourceMap in source["drumMaps"]:
        programs = []
        for program in sourceMap["programs"]:
            banks = []
            for bankIndex, bank in enumerate(program["banks"]):
                toneSet = "sc8850_%s_%d_%d_%d" % (
                    sourceMap["name"],
                    program["pc"],
                    bank["msb"],
                    bank["lsb"],
                )
                toneSets[toneSet] = {
                    int(note): name for note, name in bank["tones"].items()
                }
                banks.append(
                    {
                        "name": bank["name"],
                        "msb": bank["msb"],
                        "lsb": bank["lsb"],
                        "toneSet": toneSet,
                    }
                )
            programs.append(
                {"pc": program["pc"], "name": program["name"], "banks": banks}
            )
        maps.append(
            {
                "name": "Sound Canvas %s (MSB/LSB variations)" % sourceMap["name"],
                "programs": programs,
            }
        )
    return maps


def buildVoices():
    gmNames = readPart("gmNames.yaml")
    gm2 = readYaml("gm2Voices.yaml")["maps"][0]
    gm2["name"] = "GM2 Melody Sound Set (MSB 121)"
    voiceData = readYaml("mu128XgVoices.yaml")
    xgPrograms = []
    for pc in range(1, 129):
        name = voiceData["base"].get(str(pc), gmNames[pc - 1])
        xgPrograms.append(
            {"pc": pc, "name": name, "banks": xgVariationBanks(pc, voiceData)}
        )
    maps = [
        gm2,
        *buildScVoices(),
        {
            "name": "XG Normal Voices (MSB 0, MU128E2-documented LSB variations)",
            "programs": xgPrograms,
        },
    ]
    return maps


def kitProgram(pc, name, bank):
    return {"pc": pc, "name": name, "banks": [dict({"name": name}, **bank)]}


def buildDrums():
    gm2 = readYaml("gm2Drums.yaml")
    gm2Map = gm2["maps"][0]
    gm2Map["name"] = "GM2 Drum Kits (MSB 120)"
    gsMap = {
        "name": "GS Drum Kits (program change, bank MSB not sent)",
        "programs": [
            kitProgram(pc, name, {"toneSet": "gm2" if pc == 1 else "gm1"})
            for pc, name in gsKits
        ],
    }
    toneSets = dict(gm2["toneSets"])
    toneSets["gm1"] = gm1Tones()
    manualKits = readYaml("mu128XgDrums.yaml")
    xgPrograms = []
    xgSfxPrograms = []
    for kit in manualKits:
        toneSet = "mu128_%d_%d" % (kit["msb"], kit["pc"])
        toneSets[toneSet] = {int(note): name for note, name in kit["notes"].items()}
        program = kitProgram(
            kit["pc"], kit["name"], {"msb": kit["msb"], "lsb": 0, "toneSet": toneSet}
        )
        (xgPrograms if kit["msb"] == 127 else xgSfxPrograms).append(program)
    xgPrograms.sort(key=lambda p: p["pc"])
    xgSfxPrograms.sort(key=lambda p: p["pc"])
    xgMap = {
        "name": "XG Drum Kits (MSB 127, LSB 0; MU128E2 note transcription)",
        "programs": xgPrograms,
    }
    xgSfxMap = {
        "name": "XG SFX Drum Kits (MSB 126, LSB 0; MU128E2 note transcription)",
        "programs": xgSfxPrograms,
    }
    scMaps = buildScDrums(toneSets)
    return {"toneSets": toneSets, "maps": [gm2Map, *scMaps, xgMap, xgSfxMap]}


if __name__ == "__main__":
    writeYaml("voices.yaml", buildVoices())
    writeYaml("drums.yaml", buildDrums())
