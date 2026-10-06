import os
import re
import shutil

import yaml

rootDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
buildDir = os.path.join(rootDir, "build")
generatedDir = os.path.join(rootDir, "modules", "spessasynth", "generated")
sizeLimit = 6000
programChunk = 8


class noAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


# Files
def dump(data):
    return yaml.dump(
        data, Dumper=noAliasDumper, sort_keys=False, width=220, allow_unicode=True
    )


def writeYaml(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(dump(data))


def readBuild(name):
    with open(os.path.join(buildDir, name), encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")[:40] or "item"


def includeAll(folderName):
    return [{"include": folderName + "/*.yaml"}]


def numbered(index, total, name):
    return "%0*d-%s" % (max(2, len(str(total))), index, slug(name))


# Items
def writeItems(dirPath, items):
    for index, item in enumerate(items, 1):
        base = numbered(index, len(items), item.get("name", item.get("id")))
        path = os.path.join(dirPath, base)
        if item.get("type") == "folder" and len(dump(item)) > sizeLimit:
            writeYaml(path + ".yaml", dict(item, items=includeAll(base)))
            writeItems(path, item["items"])
        else:
            writeYaml(path + ".yaml", item)


# Maps
def writeMaps(dirPath, maps):
    for index, mapSpec in enumerate(maps, 1):
        base = numbered(index, len(maps), mapSpec["name"])
        path = os.path.join(dirPath, base)
        if len(dump(mapSpec)) <= sizeLimit:
            writeYaml(path + ".yaml", mapSpec)
            continue
        programs = mapSpec["programs"]
        writeYaml(path + ".yaml", dict(mapSpec, programs=includeAll(base)))
        for start in range(0, len(programs), programChunk):
            chunk = programs[start : start + programChunk]
            name = "%02d-pc%s-%s.yaml" % (
                start // programChunk + 1,
                chunk[0]["pc"],
                chunk[-1]["pc"],
            )
            writeYaml(os.path.join(path, name), chunk)


# Tone sets
def toneSetGroup(key):
    parts = str(key).split("_")
    return "_".join(parts[:2]) if parts[0].startswith("sc") else parts[0]


def chunkToneSets(sets):
    chunks = [{}]
    size = 0
    for key, value in sets.items():
        entrySize = len(dump({key: value}))
        if chunks[-1] and size + entrySize > sizeLimit:
            chunks.append({})
            size = 0
        chunks[-1][key] = value
        size += entrySize
    return chunks


def writeToneSets(dirPath, toneSets):
    groups = {}
    for key, value in toneSets.items():
        groups.setdefault(toneSetGroup(key), {})[key] = value
    for group, sets in groups.items():
        chunks = chunkToneSets(sets)
        for index, chunk in enumerate(chunks, 1):
            name = group if len(chunks) == 1 else "%s-%02d" % (group, index)
            writeYaml(os.path.join(dirPath, slug(name) + ".yaml"), chunk)


# Sections
def splitControls(name):
    spec = readBuild(name + ".yaml")
    writeYaml(os.path.join(generatedDir, name, "tables.yaml"), spec.get("tables", []))
    writeItems(os.path.join(generatedDir, name, "items"), spec.get("items", []))


def splitDefaults():
    spec = readBuild("defaults.yaml")
    base = os.path.join(generatedDir, "defaults")
    writeYaml(
        os.path.join(base, "header.yaml"),
        {
            key: value
            for key, value in spec.items()
            if key not in ("templates", "tracks")
        },
    )
    writeItems(os.path.join(base, "templates"), spec["templates"])
    writeItems(os.path.join(base, "tracks"), spec["tracks"])


def splitDrums():
    spec = readBuild("drums.yaml")
    writeToneSets(os.path.join(generatedDir, "drums", "toneSets"), spec["toneSets"])
    writeMaps(os.path.join(generatedDir, "drums", "maps"), spec["maps"])


if __name__ == "__main__":
    shutil.rmtree(generatedDir, ignore_errors=True)
    writeMaps(os.path.join(generatedDir, "voices"), readBuild("voices.yaml"))
    splitDrums()
    splitControls("controls")
    splitControls("effects")
    splitDefaults()
