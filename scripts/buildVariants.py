import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

scriptsDir = os.path.dirname(os.path.abspath(__file__))
rootDir = os.path.dirname(scriptsDir)
sys.path.insert(0, scriptsDir)

import genDefaults
import splitModule
from lib import ctl

moduleId = "spessasynth"
sourceDir = os.path.join(rootDir, "modules", moduleId)


def variantId(variant):
    return moduleId if variant == genDefaults.defaultVariant else "%s_%s" % (moduleId, variant.lower())


def coreVersion():
    """The spessasynth_core release the submodule is checked out at."""
    path = os.path.join(rootDir, "vendor", "spessasynth_core", "package.json")
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)["version"]
    except (OSError, KeyError, ValueError):
        raise SystemExit(
            "Cannot read the spessasynth_core version from %s. "
            "Run: git submodule update --init" % path
        )


def variantName(name, variant):
    # The module name carries the spessasynth_core version it is based on.
    name = "%s %s" % (name, coreVersion())
    if variant == genDefaults.defaultVariant:
        return name
    return "%s (%s)" % (name, variant)


def prepare(workDir, variant):
    target = os.path.join(workDir, variantId(variant))
    shutil.copytree(sourceDir, target)

    genDefaults.writeDefaults(variant)  # build/defaults.yaml
    splitModule.generatedDir = os.path.join(target, "generated")
    shutil.rmtree(os.path.join(target, "generated", "defaults"), ignore_errors=True)
    splitModule.splitDefaults()

    path = os.path.join(target, "module.yaml")
    with open(path, encoding="utf-8", newline="") as handle:
        text = handle.read()
    text, count = re.subn(
        r"^name:[ \t]*(.*?)(\r?)$",
        lambda match: "name: %s%s" % (variantName(match.group(1).strip(), variant), match.group(2)),
        text,
        count=1,
        flags=re.M,
    )
    if count != 1:
        raise SystemExit("module.yaml has no name line")
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def build(workDir, variant, outDir, version):
    args = [sys.executable, "-m", "DominoDefBuilder", "--modules", workDir, "build", variantId(variant), "--out", outDir]
    if version:
        args += ["--version", version]
    code = subprocess.call(args, cwd=rootDir)
    if code != 0:
        sys.exit(code)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("variants", nargs="*", type=str.upper, help="default data variants, all when omitted")
    parser.add_argument("--version")
    parser.add_argument("--out", default=os.path.join(rootDir, "dist"))
    options = parser.parse_args()

    unknown = [name for name in options.variants if name not in genDefaults.variantOrder]
    if unknown:
        parser.error("unknown variant: %s (use %s)" % (", ".join(unknown), ", ".join(genDefaults.variantOrder)))
    variants = [name for name in genDefaults.variantOrder if not options.variants or name in options.variants]

    shutil.rmtree(options.out, ignore_errors=True)
    os.makedirs(options.out)
    manifest = []
    with tempfile.TemporaryDirectory() as workDir:
        for variant in variants:
            partDir = os.path.join(workDir, "out-" + variant)
            prepare(os.path.join(workDir, "modules"), variant)
            build(os.path.join(workDir, "modules"), variant, partDir, options.version)
            with open(os.path.join(partDir, "manifest.json"), encoding="utf-8") as handle:
                manifest += json.load(handle)
            for name in os.listdir(partDir):
                if name.endswith(".xml"):
                    shutil.copy(os.path.join(partDir, name), options.out)
            shutil.rmtree(os.path.join(workDir, "modules", variantId(variant)))
    with open(os.path.join(options.out, "manifest.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    # Leave build/defaults.yaml as the default variant, as genAll produced it
    genDefaults.writeDefaults(genDefaults.defaultVariant)


if __name__ == "__main__":
    main()
