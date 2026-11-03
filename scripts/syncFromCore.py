import argparse
import os
import re
import subprocess
import sys

import yaml

repoDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
defaultCoreDir = os.path.join(repoDir, "vendor", "spessasynth_core")
outputPath = os.path.join(
    repoDir, "modules", "spessasynth", "generated", "effectParts", "core_data.yaml"
)

xgDir = os.path.join("src", "synthesizer", "audio_engine", "effects", "xg")
gsDir = os.path.join("src", "synthesizer", "audio_engine", "effects", "gs")


# TypeScript handling


def read(filepath):
    with open(filepath, encoding="utf-8") as handle:
        return handle.read()


def stripNoise(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    text = re.sub(r"`(?:[^`\\]|\\.)*`", '""', text)
    text = re.sub(r'"(?:[^"\\]|\\.)*"', '""', text)
    text = re.sub(r"'(?:[^'\\]|\\.)*'", "''", text)
    return text


def braceMatch(text, start):
    if text[start] != "{":
        raise ValueError("Not at a brace: %r" % text[start])
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise ValueError("Unbalanced braces")


class TsClass:
    def __init__(self, name, extends, body, raw, path):
        self.name = name
        self.extends = extends
        self.body = body
        self.raw = raw
        self.path = path


def collectClasses(dirPath):
    classes = {}
    for dirName, _, fileNames in os.walk(dirPath):
        for fileName in sorted(fileNames):
            if not fileName.endswith(".ts") or fileName.endswith(".d.ts"):
                continue
            path = os.path.join(dirName, fileName)
            raw = read(path)
            text = stripNoise(raw)
            for match in re.finditer(
                r"(?:export\s+)?(?:abstract\s+)?class\s+(\w+)"
                r"(?:\s+extends\s+(\w+))?(?:\s+implements\s+[^{]*)?\s*\{",
                text,
            ):
                name = match.group(1)
                obj = TsClass(
                    name,
                    match.group(2),
                    braceMatch(text, match.end() - 1),
                    raw,
                    path,
                )
                if name in classes:
                    raise SystemExit(
                        "Duplicate class %s in %s and %s"
                        % (name, obj.path, classes[name].path)
                    )
                classes[name] = obj
    return classes


def findFieldBody(body, name):
    match = re.search(r"readonly\s+" + name + r"\s*[^=;{]*=\s*", body)
    if match is None:
        return None
    index = match.end() - 1
    if body[index] == "{":
        return braceMatch(body, index)
    return body[index : body.index(";", index)].strip()


def fieldInChain(classes, className, name):
    current = className
    while current is not None:
        spec = classes[current]
        value = findFieldBody(spec.body, name)
        if value is not None:
            return value, spec
        current = spec.extends
    return None, None


# Literal parsers


def parseNumber(token):
    token = token.strip()
    if token.lower().startswith("0x"):
        return int(token.replace("_", ""), 16)
    return int(token)


def parseNumberList(text):
    inner = text[text.index("[") + 1 : text.rindex("]")]
    return [parseNumber(token) for token in inner.split(",") if token.strip()]


def splitTopLevel(text):
    parts = []
    depth = 0
    current = []
    for char in text:
        if char in "[(":
            depth += 1
        elif char in "])":
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current))
    return parts


def parseRangeMap(objectText, known):
    inner = objectText.strip()
    if inner.startswith("{"):
        inner = inner[1 : inner.rindex("}")]
    result = {}
    for part in splitTopLevel(inner):
        part = part.strip()
        if not part:
            continue
        if part.startswith("..."):
            spread = part[3:].strip()
            if spread not in known:
                raise KeyError(spread)
            result.update(known[spread])
            continue
        key, _, value = part.partition(":")
        result[parseNumber(key)] = parseNumberList(value)
    return result


# Ranges constants
# `ranges` fields in most DSP classes point at a `const NAME = { … };` declared
# in the same file or imported from a base class file. Several files reuse the
# same const names, so the declaring file wins across files.

SHARED_CONSTS = {}
CONST_ORIGIN = {}
FILE_CONSTS = {}


def parseFileConsts(path):
    text = stripNoise(read(path))
    matches = list(re.finditer(r"\bconst\s+(\w+)\s*[^={\n]*=\s*\{", text))
    local = {}
    for match in matches:
        local[match.group(1)] = {}
    pool = dict(SHARED_CONSTS)
    for match in matches:
        name = match.group(1)
        try:
            local[name] = parseRangeMap(braceMatch(text, match.end() - 1), pool)
        except KeyError:
            pass  # Spread not known yet; filled in by the second pass.
        pool[name] = local[name]
    for match in matches:
        name = match.group(1)
        try:
            local[name] = parseRangeMap(braceMatch(text, match.end() - 1), pool)
        except KeyError as error:
            raise SystemExit("Unresolvable spread %r in %s" % (error, path))
    for name, value in local.items():
        CONST_ORIGIN[name] = path
    FILE_CONSTS[path] = local
    return local


def fileConsts(spec):
    path = spec if isinstance(spec, str) else spec.path
    if path not in FILE_CONSTS:
        parseFileConsts(path)
    return FILE_CONSTS[path]


# XG presets

NO_PARAM_CLASSES = {"XGNoEffect", "XGThru"}


def xgDefaults(classes, className):
    value, _ = fieldInChain(classes, className, "preset")
    if value is None or "{" not in value:
        return None
    match = re.search(r"defaults\s*:\s*\[", value)
    if match is None:
        return None
    end = value.index("]", match.end())
    return parseNumberList(value[match.start() : end + 1])


def xgRanges(classes, className):
    current = className
    while current is not None:
        spec = classes[current]
        value = findFieldBody(spec.body, "ranges")
        if value is not None:
            text = value.strip()
            if text.startswith("{"):
                return parseRangeMap(text, {}), current
            local = fileConsts(spec)
            if text not in local and text in CONST_ORIGIN:
                local = fileConsts(CONST_ORIGIN[text])
            if text not in local:
                raise SystemExit(
                    "Ranges const %r not found in %s" % (text, spec.path)
                )
            return local[text], current
        current = spec.extends
    return {}, None


def parseXgMap(text, mapName):
    match = re.search(r"\b" + mapName + r"\b[\s\S]*?new Map", text)
    if match is None:
        raise SystemExit("Map %s not found" % mapName)
    start = text.index("[", match.end() - 1)
    end = text.index("])", start)
    return [
        (parseNumber(code), className)
        for code, className in re.findall(
            r"\[(0x[\da-f_]+)\s*,\s*(\w+)\]", text[start:end]
        )
    ]


def parseDefaultType(text):
    match = re.search(r"super\(\s*\w+\s*,\s*\w+\s*,\s*(0x[\da-f_]+)", text)
    return parseNumber(match.group(1)) if match else 0


def xgFilePath(coreDir, *parts):
    return os.path.join(coreDir, xgDir, *parts)


def buildXg(classes, coreDir):
    blocks = {}
    for block, fileName, mapName in (
        ("reverb", "reverb.ts", "REVERB_MAP"),
        ("chorus", "chorus.ts", "CHORUS_MAP"),
        ("variation", "variation.ts", "VARIATION_MAP"),
        ("insertion", "insertion.ts", "INSERTION_MAP"),
    ):
        text = stripNoise(read(xgFilePath(coreDir, "implementation", fileName)))
        types = []
        for code, className in parseXgMap(text, mapName):
            defaults = xgDefaults(classes, className)
            if defaults is None and className in NO_PARAM_CLASSES:
                # NO EFFECT / THRU: no preset, no parameters, all zero.
                defaults = [0] * 16
            elif defaults is None:
                raise SystemExit("No defaults for %s" % className)
            ranges, source = xgRanges(classes, className)
            types.append(
                {
                    "code": code,
                    "class": className,
                    "defaults": defaults,
                    "ranges": {str(key): pair for key, pair in sorted(ranges.items())},
                    "rangesFrom": source,
                }
            )
        blocks[block] = {"defaultType": parseDefaultType(text), "types": types}
    return blocks


# GS EFX


def gsFilePath(coreDir, *parts):
    return os.path.join(coreDir, gsDir, *parts)


def docCommentName(spec):
    match = re.search("(?:export\\s+)?(?:abstract\\s+)?class\\s+" + spec.name, spec.raw)
    if match is None:
        return spec.name
    comment = spec.raw[: match.start()]
    start = comment.rfind("/**")
    if start < 0:
        return spec.name
    # Skip the `/**` line itself.
    rest = comment[start:].split("\n", 1)[1:] or [""]
    first = re.search(r"\*\s*(.+?)\s*\n", rest[0])
    if not first:
        return spec.name
    # Drop a trailing "(CODE): description" or "(CODE)." clause.
    return re.sub(r"\s*\(`.*?`\)\s*:?\s*.*$", "", first.group(1)).strip()


def parseGsRecord(value):
    text = value.strip()
    if text.startswith("{"):
        text = text[1 : text.rindex("}") if text.endswith("}") else len(text)]
    result = {}
    for part in splitTopLevel(text):
        part = part.strip()
        if not part:
            continue
        key, _, number = part.partition(":")
        result[parseNumber(key)] = parseNumber(number)
    return result


def buildGs(coreDir):
    classes = collectClasses(gsFilePath(coreDir, "implementation", "dsp"))
    text = stripNoise(read(gsFilePath(coreDir, "implementation", "dsp", "effect_list.ts")))
    match = re.search(r"=\s*\[\s*\n", text)
    if match is None:
        raise SystemExit("GS_EFFECT_LIST not found")
    end = text.index("];", match.start())
    classNames = [n.strip() for n in text[match.end() : end].split(",") if n.strip()]
    types = []
    for className in classNames:
        spec = classes.get(className)
        if spec is None:
            raise SystemExit("GS class not found: " + className)
        typeField = findFieldBody(spec.body, "type")
        defaultsMatch = re.search(
            r"defaults\s*[^=;\n]{0,60}=\s*(?:new\s+\w+\s*\(\s*)?\[", spec.body
        )
        defaults = []
        if defaultsMatch:
            start = defaultsMatch.end() - 1
            end = spec.body.index("]", start)
            defaults = parseNumberList(spec.body[start : end + 1])
        limitsValue, _ = fieldInChain(classes, className, "limits")
        minimumsValue, _ = fieldInChain(classes, className, "minimums")
        types.append(
            {
                "code": parseNumber(typeField) if typeField else None,
                "class": className,
                "name": docCommentName(spec),
                "defaults": defaults,
                "limits": parseGsRecord(limitsValue or "{}"),
                "minimums": parseGsRecord(minimumsValue or "{}"),
            }
        )
    return {"defaultType": 0, "types": types}


# Label source tables


def findArrayNumbers(text, name, matrix=False):
    searchFrom = 0
    while True:
        found = text.find(name, searchFrom)
        if found < 0:
            raise SystemExit("Array %s not found" % name)
        head = found + len(name)
        # Only a `const` declaration counts; look for the value bracket on the
        # same line, skipping a type annotation and a typed-array constructor.
        lineEnd = text.find("\n", head)
        equal = text.find("=", head)
        if equal < 0 or (lineEnd >= 0 and equal >= lineEnd):
            searchFrom = found + 1
            continue
        probe = equal + 1
        while text[probe] in " \t\r\n":
            probe += 1
        if text[probe].isalpha():
            # `new Int8Array([...])`: the values bracket sits inside
            # the constructor's parentheses (or right after them).
            paren = text.find("(", probe)
            closeParen = text.find(")", paren)
            probe = text.find("[", paren, closeParen)
            if probe < 0:
                probe = text.find("[", closeParen)
        else:
            probe = text.find("[", probe)
        if probe < 0 or text[probe] != "[":
            searchFrom = found + 1
            continue
        start = probe
        break
    end = start
    if matrix:
        depth = 0
        for end in range(start, len(text)):
            if text[end] == "[":
                depth += 1
            elif text[end] == "]":
                depth -= 1
                if depth == 0:
                    break
    else:
        end = text.index("]", start)
    body = text[start + 1 : end]

    def toNumber(token):
        cleaned = token.replace("_", "")
        if cleaned.lower().startswith("0x"):
            return int(cleaned, 16)
        if "." in cleaned or "e" in cleaned or "E" in cleaned:
            return float(cleaned)
        return int(cleaned)

    body = "\n".join(
        line.split("//")[0] for line in body.split("\n")
    )
    if not matrix:
        return [
            toNumber(token) for token in body.replace(",", " ").split()
        ]
    rows = []
    for tokens in body.split("["):
        tokens = tokens.split("]")[0].replace(",", " ").split()
        if tokens:
            rows.append([toNumber(token) for token in tokens])
    return rows


def buildLabels(coreDir):
    dspPath = os.path.join(coreDir, xgDir, "implementation", "dsp")

    def readXg(fileName):
        return read(os.path.join(dspPath, fileName))

    xgTables = readXg("xg_dsp_tables.ts")
    erTables = readXg(os.path.join("early_reflections", "early_reflection_tables.ts"))
    labels = {
        "coefficientModes": findArrayNumbers(xgTables, "COEFFICIENT_MODES"),
        "filterFreq": findArrayNumbers(xgTables, "FILTER_FREQUENCIES"),
        "filterGain": findArrayNumbers(xgTables, "FILTER_GAIN"),
        "delayOffset": findArrayNumbers(xgTables, "DELAY_OFFSET"),
        "delayTable": findArrayNumbers(xgTables, "DELAY_TABLE"),
        "lfoRate": findArrayNumbers(xgTables, "LFO_RATE"),
        "highDampFrequency": findArrayNumbers(erTables, "HIGH_DAMP_FREQUENCY"),
    }
    conversion = read(os.path.join(
        coreDir, gsDir, "implementation", "dsp", "conversion.ts"
    ))
    labels["gsConversion"] = findArrayNumbers(conversion, "CONVERSION_TABLE", True)
    return labels
# Main


def build(coreDir):
    dspDir = xgFilePath(coreDir, "implementation", "dsp")
    for dirName, _, fileNames in os.walk(dspDir):
        for fileName in sorted(fileNames):
            if fileName.endswith(".ts") and not fileName.endswith(".d.ts"):
                parseFileConsts(os.path.join(dirName, fileName))
    classes = collectClasses(dspDir)
    xg = buildXg(classes, coreDir)
    return {"xg": xg, "gs": buildGs(coreDir)}


class NiceDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def coreRevision(coreDir):
    def git(*args):
        result = subprocess.run(
            ["git", "-C", coreDir] + list(args), capture_output=True, text=True
        )
        return result.stdout.strip() if result.returncode == 0 else None

    commit = git("rev-parse", "HEAD")
    if not commit:
        return None
    return git("describe", "--tags", "--exact-match", "HEAD") or "untagged", commit


def main():
    parser = argparse.ArgumentParser(
        description="Extract effect data from the spessasynth_core sources"
    )
    parser.add_argument(
        "--core",
        default=defaultCoreDir,
        help="Path to the spessasynth_core checkout (default: the vendor/ submodule)",
    )
    args = parser.parse_args()
    coreDir = os.path.abspath(args.core)

    revision = coreRevision(coreDir)
    if revision is None:
        sys.stderr.write(
            "%s is not a git checkout. Run: git submodule update --init\n" % args.core
        )
        return 1

    data = build(coreDir)
    data["labels"] = buildLabels(coreDir)
    summary = []
    for block, parent in sorted(data["xg"].items()):
        summary.append(
            "XG %s: %d types (default %04X)"
            % (block, len(parent["types"]), parent["defaultType"])
        )
    summary.append("GS EFX: %d types" % len(data["gs"]["types"]))

    os.makedirs(os.path.dirname(outputPath), exist_ok=True)
    with open(outputPath, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            yaml.dump(
                data, Dumper=NiceDumper, sort_keys=False, width=880, default_flow_style=None
            )
        )
    print(
        "Wrote %s for spessasynth_core %s %s (%s)"
        % (os.path.relpath(outputPath, repoDir), revision[0], revision[1][:7], "; ".join(summary))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
