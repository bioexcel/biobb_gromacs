# Biobb GROMACS changelog

## What's new in version [4.2.0](https://github.com/bioexcel/biobb_gromacs/releases/tag/v4.2.0)?

### Changes

* [DOCS] Adding fair software badge and GA
* [FIX] Fixing type hints problems
* [FIX] Type Hints Errors
* [DOCS] Adding CITATION.cff in paths-ignore
* [DOCS] Howfairis checker
* [DOCS] Adding CITATION.cff and badges to the readme
* [CI/CD] Adding Castiel Gitlab push sync github Action


## What's new in version [4.1.1](https://github.com/bioexcel/biobb_gromacs/releases/tag/v4.1.1)?

### New features

* Check for GROMACS version now raises a warning instead of an Exception.

## What's new in version [4.1.0](https://github.com/bioexcel/biobb_gromacs/releases/tag/v4.1.0)?

### New features

* TRR file output is now optional in mdrun.
* Extended functionality and usage of gmx_check.


## What's new in version [4.0.0](https://github.com/bioexcel/biobb_gromacs/releases/tag/v4.0.0)?

### New features

* New biobb_common new properties and features there.
* New GROMACS default version 2022.4


## What's new in version [3.9.0](https://github.com/bioexcel/biobb_gromacs/releases/tag/v3.9.0)?

### New features

* All inputs/outputs are checked for correct file format, extension and type (general)


## What's new in version [3.8.1](https://github.com/bioexcel/biobb_gromacs/releases/tag/v3.8.1)?

### New features

* New Trjcat block (general)



## What's new in version [3.8.0](https://github.com/bioexcel/biobb_gromacs/releases/tag/v3.8.0)?
In version 3.8.0 the default GROMACS version will be v2022.2

### New features

* Update to biobb_common 3.8.1 (general)


## What's new in version [3.7.1](https://github.com/bioexcel/biobb_gromacs/releases/tag/v3.7.1)?

### Bug fixes

* Problem with Gmx version check (mdrun) [#48](https://github.com/bioexcel/biobb_gromacs/issues/48)

## What's new in version [3.7.0](https://github.com/bioexcel/biobb_gromacs/releases/tag/v3.7.0)?
In version 3.7.0 the dependency biobb_common has been updated to 3.7.0 version.

### New features

* Update to biobb_common 3.7.0 (general)

## What's new in version [3.6.0](https://github.com/bioexcel/biobb_gromacs/releases/tag/v3.6.0)?
In version 3.6.0 Python has been updated to version 3.7 and Biopython to version 1.79.
Big changes in the documentation style and content. Finally a new conda installation recipe has been introduced.

### New features

* Update to Python 3.7 (general)
* Update to Biopython 1.79 (general)
* New conda installer (installation)
* Adding type hinting for easier usage (API)
* Deprecating os.path in favour of pathlib.path (modules)
* New command line documentation (documentation)

### Bug fixes

* Replace container Quay.io badge (documentation)
* Remove unused system and step arguments from command line causing execution errors (cli) [#9](https://github.com/bioexcel/biobb_model/issues/9)

### Other changes

* New documentation styles (documentation) [#8](https://github.com/bioexcel/biobb_model/issues/8)
