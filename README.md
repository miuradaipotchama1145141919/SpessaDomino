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

This writes every default data variant to dist (see below). Copy the one you want into the Domino Module folder. Domino lists them by name, so installing several at once works, for example "SpessaSynth" and "SpessaSynth (SSGM1)".

Build a single variant, or set the version:

```
python scripts/buildVariants.py SSGM1
python scripts/buildVariants.py --version 1.0
```

## Default data variants

The default data is the starter project a new Domino file opens with: a System Setup track and CH01 to CH16 setup. It comes in eight variants. SS stands for SpessaSynth, and SS itself is the GS hybrid, so there is no separate SSGS.

| Variant | File | Starter project |
| --- | --- | --- |
| SS (default) | spessasynth.xml | GS plus the 14 bit controls (the GS hybrid) |
| GM1 | spessasynth_gm1.xml | Strict GM1 |
| GM2 | spessasynth_gm2.xml | Strict GM2 |
| GS | spessasynth_gs.xml | Strict Roland GS |
| XG | spessasynth_xg.xml | Strict Yamaha XG |
| SSGM1 | spessasynth_ssgm1.xml | GM1 plus the 14 bit controls |
| SSGM2 | spessasynth_ssgm2.xml | GM2 plus the 14 bit controls |
| SSXG | spessasynth_ssxg.xml | XG plus the 14 bit controls |

Only the starter project and the module name differ. Every variant contains all voices, drums, controls, effects and the same template list, which holds a System Setup and a Channel Init template for each of the eight variants.

The strict variants keep only the 14 bit data their standard defines. The 14 bit channel volume, pan and expression controls (CC 7, 10, 11 with LSB CC 39, 42, 43) are optional and appear only in the SS variants.

These hybrid variants and templates are purely meant for SpessaSynth. Other synthesizers will likely read the 14 bit LSB controllers as extra, unrelated, or completely ignore the MIDI messages.

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

In the default SS variant, new projects open in GS mode. A System Setup track sends GS Reset, and channels 1 to 16 are initialized from the SpessaSynth Channel Init template, with channel 10 as the rhythm track. The template list also has System Setup and Channel Init templates for GM1, GM2 and XG.

## Control Macro Change (CCM) restoration

> **Disclaimer.** When Domino restores Control Change Macros while importing an existing MIDI file, parts of the MIDI such as its volume and program changes can be recovered oddly or inaccurately. This cannot be avoided: this module covers many standards and maps (GM1, GM2, GS, XG, the SC maps and 14 bit controls), which makes Domino's automatic process guess wrong more often. Projects made from scratch in Domino do not have this problem, because no restoration is needed.

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

`ci` regenerates, validates and builds all eight variants on every push to `main` and on pull requests, on Python 3.10 and 3.14. The built XML and the generated sources are attached to the run as artifacts.

## Releases

Push a tag such as `v0.9`. The `release` workflow rebuilds with the tag (without the `v`) as the module version and attaches every variant XML (`spessasynth.xml`, `spessasynth_ssgm1.xml` and so on), `manifest.json` and `generated.zip` to a GitHub Release.

```
git tag v0.9
git push origin v0.9
```
