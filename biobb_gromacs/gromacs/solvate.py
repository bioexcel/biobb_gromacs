#!/usr/bin/env python3

"""Module containing the Editconf class and the command line interface."""
import shutil
import argparse
from typing import Optional
from pathlib import Path
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_gromacs.gromacs.common import get_gromacs_version


class Solvate(BiobbObject):
    """
    | biobb_gromacs Solvate
    | Wrapper of the `GROMACS solvate <http://manual.gromacs.org/current/onlinehelp/gmx-solvate.html>`_ module.
    | The GROMACS solvate module, generates a box of solvent around the selected structure.

    Args:
        input_solute_gro_path (str): Path to the input GRO file. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/solvate.gro>`_. Accepted formats: gro (edam:format_2033), pdb (edam:format_1476).
        output_gro_path (str): Path to the output GRO file. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_solvate.gro>`_. Accepted formats: gro (edam:format_2033), pdb (edam:format_1476).
        input_top_zip_path (str): Path the input TOP topology in zip format. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/solvate.zip>`_. Accepted formats: zip (edam:format_3987).
        output_top_zip_path (str): Path the output topology in zip format. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_solvate.zip>`_. Accepted formats: zip (edam:format_3987).
        input_solvent_gro_path (str) (Optional): (spc216.gro) Path to the GRO file containing the structure of the solvent. File type: input. Accepted formats: gro (edam:format_2033).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **shell** (*float*) - (0.0) [0~100|0.1] Thickness in nanometers of optional water layer around solute.
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
            * version: 2024.5
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_solute_gro_path: str, output_gro_path: str, input_top_zip_path: str,
                 output_top_zip_path: str, input_solvent_gro_path: Optional[str] = None, properties: Optional[dict] = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_solute_gro_path": input_solute_gro_path, "input_solvent_gro_path": input_solvent_gro_path},
            "out": {"output_gro_path": output_gro_path, "output_top_zip_path": output_top_zip_path}
        }

        # Should not be copied inside container
        self.input_top_zip_path = input_top_zip_path

        # Properties specific for BB
        self.shell = properties.get('shell')
        if not self.io_dict["in"].get('input_solvent_gro_path'):
            self.io_dict["in"]['input_solvent_gro_path'] = 'spc216.gro'

        # Properties common in all GROMACS BB
        self.gmx_lib = properties.get('gmx_lib', None)
        self.binary_path = properties.get('binary_path', 'gmx')
        self.gmx_nobackup = properties.get('gmx_nobackup', True)
        self.gmx_nocopyright = properties.get('gmx_nocopyright', True)
        if self.gmx_nobackup:
            self.binary_path += ' -nobackup'
        if self.gmx_nocopyright:
            self.binary_path += ' -nocopyright'
        if not self.container_path:
            self.gmx_version = get_gromacs_version(self.binary_path)

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Solvate <gromacs.solvate.Solvate>` object."""

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        # Unzip topology to topology_out
        top_file = fu.unzip_top(zip_file=self.input_top_zip_path, out_log=self.out_log)
        top_dir = str(Path(top_file).parent)

        if self.container_path:
            shutil.copytree(top_dir, str(Path(self.stage_io_dict.get("unique_dir", "")).joinpath(Path(top_dir).name)))
            top_file = str(Path(self.container_volume_path).joinpath(Path(top_dir).name, Path(top_file).name))

        self.cmd = [self.binary_path, 'solvate',
                    '-cp', self.stage_io_dict["in"]["input_solute_gro_path"],
                    '-cs', self.stage_io_dict["in"]["input_solvent_gro_path"],
                    '-o', self.stage_io_dict["out"]["output_gro_path"],
                    '-p', top_file]

        if self.shell:
            self.cmd.append("-shell")
            self.cmd.append(str(self.shell))

        if self.gmx_lib:
            self.env_vars_dict['GMXLIB'] = self.gmx_lib

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        if self.container_path:
            top_file = str(Path(self.stage_io_dict.get("unique_dir", "")).joinpath(Path(top_dir).name, Path(top_file).name))

        # zip topology
        fu.log('Compressing topology to: %s' % self.stage_io_dict["out"]["output_top_zip_path"], self.out_log,
               self.global_log)
        fu.zip_top(zip_file=self.io_dict["out"]["output_top_zip_path"], top_file=top_file, out_log=self.out_log, remove_original_files=self.remove_tmp)

        # Remove temporal files
        # self.tmp_files.extend([self.stage_io_dict.get("unique_dir", ""), top_dir])
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)
        return self.return_code


def solvate(input_solute_gro_path: str, output_gro_path: str, input_top_zip_path: str,
            output_top_zip_path: str, input_solvent_gro_path: Optional[str] = None, properties: Optional[dict] = None, **kwargs) -> int:
    """Create :class:`Solvate <gromacs.solvate.Solvate>` class and
    execute the :meth:`launch() <gromacs.solvate.Solvate.launch>` method."""

    return Solvate(input_solute_gro_path=input_solute_gro_path, output_gro_path=output_gro_path,
                   input_top_zip_path=input_top_zip_path, output_top_zip_path=output_top_zip_path,
                   input_solvent_gro_path=input_solvent_gro_path, properties=properties, **kwargs).launch()


solvate.__doc__ = Solvate.__doc__


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Wrapper for the GROMACS solvate module.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('-c', '--config', required=False, help="This file can be a YAML file, JSON file or JSON string")

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_solute_gro_path', required=True)
    required_args.add_argument('--output_gro_path', required=True)
    required_args.add_argument('--input_top_zip_path', required=True)
    required_args.add_argument('--output_top_zip_path', required=True)
    parser.add_argument('--input_solvent_gro_path', required=False)

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    solvate(input_solute_gro_path=args.input_solute_gro_path, output_gro_path=args.output_gro_path,
            input_top_zip_path=args.input_top_zip_path, output_top_zip_path=args.output_top_zip_path,
            input_solvent_gro_path=args.input_solvent_gro_path, properties=properties)


if __name__ == '__main__':
    main()
