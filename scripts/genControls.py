import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.ctl import colorize, writeYaml
from genGs import buildGs
from genStandard import buildStandard
from genXg import buildXg
from genDefaults import writeDefaults


def merge(parts):
    return {
        "tables": [table for part in parts for table in part.get("tables", [])],
        "items": [item for part in parts for item in part.get("items", [])],
    }


if __name__ == "__main__":
    writeYaml("controls.yaml", colorize(merge([buildStandard()])))
    writeYaml("effects.yaml", colorize(merge([buildGs(), buildXg()])))
    writeDefaults()
