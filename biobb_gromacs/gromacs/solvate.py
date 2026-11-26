#!/usr/bin/env python3

"""Module containing the Editconf class and the command line interface."""
from typing import Optional
from pathlib import PurePath
from biobb_common.generic.biobb_object import launcher
from biobb_common.tools import file_utils as fu
from biobb_gromacs.gromacs.common import GromacsBlock


class Solvate(GromacsBlock):
    """
    | biobb_gromacs Solvate
    | Wrapper of the `GROMACS solvate <http://manual.gromacs.org/current/onlinehelp/gmx-solvate.html>`_ module.
    | The GROMACS solvate module, generates a box of solvent around the selected structure.

    Args:
        input_solute_gro_path (str): Path to the input GRO file. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/solvate.gro>`_. Accepted formats: gro (edam:format_2033), pdb (edam:format_1476).
        output_gro_path (str): Path to the output GRO file. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_solvate.gro>`_. Accepted formats: gro (edam:format_2033), pdb (edam:format_1476).
        input_top_zip_path (str): Path the input TOP topology in zip format. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/solvate.zip>`_. Accepted formats: zip (edam:format_3987).
        output_top_zip_path (str): Path the output topology in zip format. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_solvate.zip>`_. Accepted formats: zip (edam:format_3987).
        input_solvent_gro_path (str) (Optional): (spc216.gro) Path to the GRO file containing the structure of the solvent. If not provided, the GROMACS solvent box selected with the solvent property is used. File type: input. Accepted formats: gro (edam:format_2033).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **solvent** (*str*) - ("spc216") GROMACS default solvent box used when input_solvent_gro_path is not provided. Values: spc216 (equilibrated 3-point water box for SPC, SPC/E and TIP3P water models), tip4p (equilibrated 4-point water box for TIP4P water models), tip5p (equilibrated 5-point water box for the TIP5P water model).
            * **shell** (*float*) - (None) [0~100|0.1] Thickness in nanometers of optional water layer around solute.
            * **gmx_lib** (*str*) - (None) Path set GROMACS GMXLIB environment variable.
            * **binary_path** (*str*) - ("gmx") Path to the GROMACS executable binary.
            * **gmx_nobackup** (*bool*) - (True) Add the -nobackup flag: GROMACS overwrites the existing files without backing them up.
            * **gmx_nocopyright** (*bool*) - (True) Add the -nocopyright flag: GROMACS does not print its copyright and citation header.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.
            * **container_path** (*str*) - (None)  Path to the binary executable of your container.
            * **container_image** (*str*) - ("gromacs/gromacs:latest") Container Image identifier.
            * **container_volume_path** (*str*) - ("/data") Path to an internal directory in the container.
            * **container_user_id** (*str*) - (None) User number id to be mapped inside the container.
            * **container_shell_path** (*str*) - ("/bin/bash") Path to the binary executable of the container shell.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_gromacs.gromacs.solvate import Solvate
            prop = { 'shell': 1.0 }
            solvate(input_solute_gro_path='/path/to/myStructure.gro',
                    output_gro_path='/path/to/newStructure.gro',
                    input_top_zip_path='/path/to/myTopology.zip',
                    output_top_zip_path='/path/to/newTopology.zip',
                    properties=prop)


    Info:
        * wrapped_software:
            * name: GROMACS Solvate
            * version: 2025.2
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_solute_gro_path: str, output_gro_path: str, input_top_zip_path: str,
                 output_top_zip_path: str, input_solvent_gro_path: Optional[str] = None, properties: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**locals())

        # Should not be copied inside container
        self.input_top_zip_path = self.io_dict["in"].pop("input_top_zip_path")

        # Properties specific for BB
        if not self.io_dict["in"].get('input_solvent_gro_path'):
            # GROMACS default solvent box, found by gmx in its library (GMXLIB) path
            self.io_dict["in"]['input_solvent_gro_path'] = str(PurePath(self.solvent).with_suffix('.gro'))

    def run(self) -> None:
        """Execute the :class:`Solvate <gromacs.solvate.Solvate>` object."""

        # Unzip the topology in the sandbox
        top_file = fu.unzip_top(zip_file=self.input_top_zip_path, out_log=self.out_log, unique_dir=self.stage_io_dict.get("unique_dir", ""))

        self.cmd = [self.binary_path, 'solvate',
                    '-cp', self.stage_io_dict["in"]["input_solute_gro_path"],
                    '-cs', self.stage_io_dict["in"]["input_solvent_gro_path"],
                    '-o', self.stage_io_dict["out"]["output_gro_path"],
                    '-p', self.staged_path(top_file)]

        if self.shell:
            self.cmd.append("-shell")
            self.cmd.append(str(self.shell))

        # Run Biobb block
        self.run_biobb()

        # zip topology
        fu.log('Compressing topology to: %s' % self.stage_io_dict["out"]["output_top_zip_path"], self.out_log,
               self.global_log)
        fu.zip_top(zip_file=self.sandbox_file("output_top_zip_path"), top_file=top_file, out_log=self.out_log, remove_original_files=self.remove_tmp)


solvate = launcher(Solvate)


if __name__ == '__main__':
    Solvate.main()
