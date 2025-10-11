# Biobb GROMACS changelog

## What's new in version [5.1.1](https://github.com/bioexcel/biobb_gromacs/releases/tag/v5.1.1)?

### Changes
* [UPDATE] Update gromacs version to 2025.2
* [FIX](https://github.com/bioexcel/biobb_gromacs/commit/5c429081aeaae513b61bc273aec2e6c67ff15dce): Fixed make_ndx stdin bug

## What's new in version [5.1.0](https://github.com/bioexcel/biobb_gromacs/releases/tag/v5.1.0)?

### Changes
* [FEATURE](https://github.com/bioexcel/biobb_gromacs/commit/acf09cbc4d4fa5dc5f2db8dee29434e313601beb): Append_ligand: take into account [ atomtype ] section when including itp files
* [FIX](https://github.com/bioexcel/biobb_gromacs/commit/aa6afa4b4346f800d00b5d86d0ba7d342ed74cdc): Avoid defining variable twice
* [FIX](https://github.com/bioexcel/biobb_gromacs/commit/db9a0a62bc38214e5aaeed9b61d1eafb6ad1e8f3): ndx2resttop: fixed index_dic creation
* [FEATURE](https://github.com/bioexcel/biobb_gromacs/commit/c3e9cd901bae89f087e8f5efdfaea8b981533b45): ndx2resttop: added custom posres name
* [FIX](https://github.com/bioexcel/biobb_gromacs/commit/1bcc746b60b6555cc244c086ab3483797e5c52bf): Take into account single chain situations with just a .top file
* [FIX](https://github.com/bioexcel/biobb_gromacs/commit/60f8d26e9495b41cd49797ee33ea5e8c59edfe53): ndx2resttop: clean mdp keywords before merging to avoid duplicates
* [FEATURE](https://github.com/bioexcel/biobb_gromacs/commit/4681ed7c380c2f83970da1280866c8eb414945b7): pdb2gmx: extend the interactive choice of protonation state for all titratable residues
* [FEATURE](https://github.com/bioexcel/biobb_gromacs/commit/your_commit_hash): pdb2gmx: support multi chain PDBs when titrating
* [FIX](https://github.com/bioexcel/biobb_gromacs/commit/762b3a6fcad3b2ad3238212c1190470ce2245b80): genion: fix default concentration 
* [UPDATE] Update gromacs version to 2024.5

## What's new in version [5.0.0](https://github.com/bioexcel/biobb_gromacs/releases/tag/v5.0.0)?

### Changes

* [CI/CD](env.yaml): Update biobb_common version.
* [Typing](ALL): Update typing from python 3.8 style to python 3.9
* [CI/CD](conf.yml): Adding global properties to test yaml configuration
* [CI/CD](linting_and_testing.yaml): Update GA test workflow to Python >3.9
* [DOCS](.readthedocs.yaml): Updating to Python 3.9
* [CI/CD](GITIGNORE): Update .gitignore to include the new file extensions to ignore
* [CI/CD](conf.yml): Change test conf.yml to adapt to new settings configuration
* [CI/CD](py.typed): Adding the py.typed
* [FIX] Adding execution permissions to append_ligand
* [UPDATE] Adding sandbox_path property to the json schemas
* [FEATURE] New sandbox_path property
* [CI/CD] Update grompp reference files and GA WF

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
