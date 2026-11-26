#!/usr/bin/env python3

"""Module containing the InsertMolecules class and the command line interface."""

from pathlib import PurePath
from typing import Optional

from biobb_common.generic.biobb_object import BiobbObject, launcher
from biobb_common.tools import file_utils as fu

from biobb_gromacs.gromacs.common import get_gromacs_version


class InsertMolecules(BiobbObject):
    """
    | biobb_gromacs InsertMolecules
    | Wrapper of the `GROMACS insert-molecules <http://manual.gromacs.org/current/onlinehelp/gmx-insert-molecules.html>`_ module.
    | The GROMACS insert-molecules module inserts copies of a molecule into the vacant space of an existing structure or into an empty box, ie to build mixed solvent boxes. The topology is not modified: the inserted molecules must be added to it afterwards.

    Args:
        input_insert_gro_path (str): Path to the GRO file of the molecule to insert. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/insert_molecules.gro>`_. Accepted formats: gro (edam:format_2033), pdb (edam:format_1476).
        output_gro_path (str): Path to the output GRO file. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_insert_molecules.gro>`_. Accepted formats: gro (edam:format_2033), pdb (edam:format_1476).
        input_gro_path (str) (Optional): Path to the GRO file of the existing structure to insert into. If not provided, the molecules are inserted into an empty box defined by the box property. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/solvate.gro>`_. Accepted formats: gro (edam:format_2033), pdb (edam:format_1476).
        input_positions_dat_path (str) (Optional): Path to the DAT file with the predefined insertion trial positions (three columns x y z in nm, displacements from the position of the molecule to insert). File type: input. Accepted formats: dat (edam:format_1637), txt (edam:format_2330).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **nmol** (*int*) - (1) [1~100000|1] Number of extra molecules to insert. Ignored if input_positions_dat_path is provided: one molecule is inserted per position.
            * **box** (*str*) - (None) Box size in nm as three floats ie "5.0 5.0 5.0". Mandatory if input_gro_path is not provided; if both are provided, a new box is placed around the input structure before the insertions.
            * **tries** (*int*) - (10) [1~10000|1] Number of insertion attempts per molecule (nmol * tries attempts are made before giving up).
            * **seed** (*int*) - (1993) Seed for random number generator (0 means generate a random seed).
            * **radius** (*float*) - (0.105) [0~10|0.001] Default van der Waals distance in nm, used for atoms not found in the vdwradii.dat database.
            * **scale** (*float*) - (0.57) [0~10|0.01] Scale factor to multiply the van der Waals radii from the vdwradii.dat database.
            * **dr** (*str*) - ("0 0 0") Allowed displacement in nm in x y z from the positions in the input_positions_dat_path file.
            * **rot** (*str*) - ("xyz") Rotate the inserted molecules randomly. Values: xyz (random rotation around all axes), z (random rotation around the z axis), none (no rotation).
            * **gmx_lib** (*str*) - (None) Path set GROMACS GMXLIB environment variable.
            * **binary_path** (*str*) - ("gmx") Path to the GROMACS executable binary.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.
            * **container_path** (*str*) - (None)  Path to the binary executable of your container.
            * **container_image** (*str*) - ("gromacs/gromacs:latest") Container Image identifier.
            * **container_volume_path** (*str*) - ("/data") Path to an internal directory in the container.
            * **container_working_dir** (*str*) - (None) Path to the internal CWD in the container.
            * **container_user_id** (*str*) - (None) User number id to be mapped inside the container.
            * **container_shell_path** (*str*) - ("/bin/bash") Path to the binary executable of the container shell.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_gromacs.gromacs.insert_molecules import insert_molecules
            prop = { 'nmol': 10,
                     'seed': 1993 }
            insert_molecules(input_insert_gro_path='/path/to/molecule.gro',
                             output_gro_path='/path/to/newStructure.gro',
                             input_gro_path='/path/to/myStructure.gro',
                             properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS insert-molecules
            * version: 2025.2
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_insert_gro_path: str, output_gro_path: str, input_gro_path: Optional[str] = None,
                 input_positions_dat_path: Optional[str] = None, properties: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**locals())

        # Properties common in all GROMACS BB
        self.gmx_nobackup = self.properties.get('gmx_nobackup', True)
        self.gmx_nocopyright = self.properties.get('gmx_nocopyright', True)
        if self.gmx_nobackup:
            self.binary_path += ' -nobackup'
        if self.gmx_nocopyright:
            self.binary_path += ' -nocopyright'
        if not self.container_path:
            self.gmx_version = get_gromacs_version(self.binary_path)

    def prepare(self) -> None:
        """Checks all the input/output paths and parameters"""
        if not self.io_dict["in"].get("input_gro_path") and not self.box:
            raise ValueError("Either input_gro_path or the box property must be provided to insert the molecules into.")

    def run(self) -> None:
        """Execute the :class:`InsertMolecules <gromacs.insert_molecules.InsertMolecules>` object."""

        if self.container_path:
            working_dir = self.container_volume_path if self.container_volume_path else "/data"
        else:
            working_dir = self.stage_io_dict.get('unique_dir', '')

        self.cmd = ["cd", working_dir, ";",
                    self.binary_path, 'insert-molecules',
                    '-ci', PurePath(self.stage_io_dict["in"]["input_insert_gro_path"]).name,
                    '-o', PurePath(self.stage_io_dict["out"]["output_gro_path"]).name,
                    '-nmol', str(self.nmol),
                    '-try', str(self.tries),
                    '-seed', str(self.seed),
                    '-radius', str(self.radius),
                    '-scale', str(self.scale),
                    '-rot', self.rot]

        if self.stage_io_dict["in"].get("input_gro_path"):
            self.cmd.append('-f')
            self.cmd.append(PurePath(self.stage_io_dict["in"]["input_gro_path"]).name)

        if self.box:
            if not isinstance(self.box, str):
                self.box = " ".join(map(str, self.box))
            self.cmd.append('-box')
            self.cmd.append(self.box)

        if self.stage_io_dict["in"].get("input_positions_dat_path"):
            if not isinstance(self.dr, str):
                self.dr = " ".join(map(str, self.dr))
            self.cmd.append('-ip')
            self.cmd.append(PurePath(self.stage_io_dict["in"]["input_positions_dat_path"]).name)
            self.cmd.append('-dr')
            self.cmd.append(self.dr)
            fu.log("Inserting one molecule per position of the positions file", self.out_log, self.global_log)
        else:
            fu.log(f"Inserting {self.nmol} molecules with seed {self.seed}", self.out_log, self.global_log)

        if self.gmx_lib:
            self.env_vars_dict['GMXLIB'] = self.gmx_lib

        # Run Biobb block
        self.run_biobb()


insert_molecules = launcher(InsertMolecules)


if __name__ == '__main__':
    InsertMolecules.main()
