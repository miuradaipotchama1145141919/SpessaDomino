import os
import subprocess
import sys

rootDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scriptsDir = os.path.join(rootDir, "scripts")

steps = [
    [os.path.join(scriptsDir, "genBanks.py")],
    [os.path.join(scriptsDir, "genControls.py")],
    [os.path.join(scriptsDir, "splitModule.py")],
    ["-m", "DominoDefBuilder", "--modules", "modules", "validate"],
    ["-m", "DominoDefBuilder", "--modules", "modules", "build"],
]


def run(args):
    print("> " + " ".join(os.path.basename(arg) for arg in args))
    return subprocess.call([sys.executable] + args, cwd=rootDir)


if __name__ == "__main__":
    for step in steps:
        code = run(step)
        if code != 0:
            sys.exit(code)
