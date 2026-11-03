# SpessaDomino

A Domino sound source definition for SpessaSynth, generated with [DominoDefBuilder](https://github.com/miuradaipotchama1145141919/DominoDefBuilder). It is based on the [SpessaSynth core v4-4-0 branch](https://github.com/spessasus/spessasynth_core/tree/v4-4-0).

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

New projects open in GS mode. A System Setup track sends GS Reset, and channels 1 to 16 are initialized from the GS Channel Init template, with channel 10 as the rhythm track. The template list also has System Setup and Channel Init templates for GM1, GM2 and XG.

## Effect coverage

The effect definitions come straight from the SpessaSynth source. XG reverb, chorus, variation and insertion effects expose every type the synth implements with per-type parameter defaults, and the GS insertion effect (EFX) has all 65 types with their parameters, send levels and EFX control sources.

## Continuous integration

`ci` regenerates, validates and builds the definition on every push to `main` and on pull requests, on Python 3.10 and 3.14. The built XML is attached to the run as an artifact.

## Releases

Push a tag such as `v0.9`. The `release` workflow rebuilds with the tag (without the `v`) as the module version and attaches `spessasynth.xml` and `manifest.json` to a GitHub Release.

```
git tag v0.9
git push origin v0.9
```
