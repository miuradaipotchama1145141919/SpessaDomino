# SpessaDomino

A Domino sound source definition for SpessaSynth, generated with [DominoDefBuilder](https://github.com/miuradaipotchama1145141919/DominoDefBuilder). It is based on [spessasynth_core](https://github.com/spessasus/spessasynth_core).

## Installation

Requires Python 3.10 or newer.

```
pip install DominoDefBuilder pyyaml
```

## Usage

Regenerate, validate and build everything with one command.

```
python scripts/genAll.py
```

The definition is written to dist/spessasynth.xml. Copy it into the Domino Module folder.

## Instrument coverage

| Map | Melody | Drums |
| --- | --- | --- |
| GM1 | Yes | Yes |
| GM2 | Yes | Yes |
| Sound Canvas 55Map | Yes | Yes |
| Sound Canvas 88Map | Yes | Yes |
| Sound Canvas 88ProMap | Yes | Yes |
| Sound Canvas 8850Map | Yes | Yes |
| XG normal voices and kits | Yes | Yes |
| XG SFX | Yes | Yes |

## Starter project

New projects open in GS mode. A System Setup track sends GS Reset, and channels 1 to 16 are initialized from the SpessaSynth Channel Init template, with channel 10 as the rhythm track. The template list also has System Setup and Channel Init templates for GM1, GM2 and XG.

## Effect coverage

Effect definitions come straight from spessasynth_core. XG reverb, chorus, variation and insertion effects expose every type the synth implements with per-type parameter defaults, and the GS insertion effect (EFX) has all 65 types with their parameters, send levels and EFX control sources.

## spessasynth_core

The synth source is now a git submodule in `vendor/spessasynth_core`, pinned to a release tag. Everything needed to regenerate the module offline is in a recursive clone:

```
git clone --recurse-submodules https://github.com/miuradaipotchama1145141919/SpessaDomino
```

If you cloned without it: `git submodule update --init`.

## Updating for a new spessasynth_core release

```
git -C vendor/spessasynth_core fetch --tags
git -C vendor/spessasynth_core checkout v4.5.0
python scripts/genAll.py
git add vendor/spessasynth_core
```

`genAll.py` starts by extracting the effect data from the submodule. `emitParts.py` stops with a list when the synth clamps a parameter that no slot list names, so a changed parameter cannot go missing silently.

## Generated files

Everything that `genAll.py` produces is git-ignored: `modules/spessasynth/generated/` (including the effect data extracted from the core), `build/` and `dist/`. CI uploads `dist` and the generated sources as artifacts.

## Continuous integration

`ci` regenerates, validates and builds the definition on every push to `main` and on pull requests, on Python 3.10 and 3.14. The built XML and the generated sources are attached to the run as artifacts.

## Releases

Push a tag such as `v0.9`. The `release` workflow rebuilds with the tag (without the `v`) as the module version and attaches `spessasynth.xml`, `manifest.json` and `generated.zip` to a GitHub Release.

```
git tag v0.9
git push origin v0.9
```
