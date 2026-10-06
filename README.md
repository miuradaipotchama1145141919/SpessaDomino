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
| GM1 | Yes | No |
| GM2 | Yes | Yes |
| Sound Canvas 55Map | Yes | Yes |
| Sound Canvas 88Map | Yes | Yes |
| Sound Canvas 88ProMap | Yes | Yes |
| Sound Canvas 8850Map | Yes | Yes |
| XG normal voices and kits | Yes | Yes |
| XG SFX | Yes | Yes |

## Starter project

New projects open in GS mode. A System Setup track sends GS Reset, and channels 1 to 16 are initialized from the GS Channel Init template, with channel 10 as the rhythm track. The template list also has System Setup and Channel Init templates for GM1, GM2 and XG.

## Experimental features

Some features exist only in the SpessaSynth 4.4.0 experimental branch and are marked Experimental in their names and memos. These are XG effects and insertion effects, the XG controller depth matrix, AC1 and AC2 numbers, and XG part dry level and portamento.

## Continuous integration

`ci` regenerates, validates and builds the definition on every push to `main` and on pull requests, on Python 3.10 and 3.14. The built XML is attached to the run as an artifact.

## Releases

Push a tag such as `v0.8`. The `release` workflow rebuilds with the tag (without the `v`) as the module version and attaches `spessasynth.xml` and `manifest.json` to a GitHub Release.

```
git tag v0.8
git push origin v0.8
```
