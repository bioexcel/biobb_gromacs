#!/usr/bin/env python3

"""Module containing the Trjcat class and the command line interface."""
import shutil
import argparse
from typing import Optional
from pathlib import Path
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_gromacs.gromacs.common import get_gromacs_version


class Trjcat(BiobbObject):
    """
    | biobb_gromacs Trjcat
    | Wrapper class for the `GROMACS trjcat <http://manual.gromacs.org/current/onlinehelp/gmx-trjcat.html>`_ module.
    | The GROMACS solvate module generates a box around the selected structure.

    Args:
        input_trj_zip_path (str): Path the input GROMACS trajectories (xtc, trr, cpt, gro, pdb, tng) to concatenate in zip format. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/trjcat.zip>`_. Accepted formats: zip (edam:format_3987).
        output_trj_path (str): Path to the output trajectory file. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_trjcat.trr>`_. Accepted formats: pdb (edam:format_1476), gro (edam:format_2033), xtc (edam:format_3875), trr (edam:format_3910), tng (edam:format_3876).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **concatenate** (*bool*) - (True) Only concatenate the files without removal of frames with identical timestamps.
            * **gmx_lib** (*str*) - (None) Path set GROMACS GMXLIB environment variable.
            * **binary_path** (*str*) - ("gmx") Path to the GROMACS executable binary.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.
            * **container_path** (*str*) - (None)  Path to the binary executable of your container.
            * **container_image** (*str*) - (None) Container Image identifier.
            * **container_volume_path** (*str*) - ("/data") Path to an internal directory in the container.
            * **container_working_dir** (*str*) - (None) Path to the internal CWD in the container.
            * **container_user_id** (*str*) - (None) User number id to be mapped inside the container.
            * **container_shell_path** (*str*) - ("/bin/bash") Path to the binary executable of the container shell.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_gromacs.gromacs.trjcat import trjcat
            prop = { 'concatenate': True }
            trjcat(input_trj_zip_path='/path/to/trajectory_bundle.zip',
                   output_gro_path='/path/to/concatenated_trajectories.xtc',
                   properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS trjcat
            * version: 2024.5
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_trj_zip_path: str, output_trj_path: str, properties: Optional[dict] = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict: dict = {
            "in": {},
            "out": {"output_trj_path": output_trj_path}
        }

        # Should not be copied inside container
        self.input_trj_zip_path = input_trj_zip_path

        # Properties specific for BB
        self.concatenate: bool = properties.get('concatenate', True)

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
        """Execute the :class:`Trjcat <gromacs.trjcat.Trjcat>` object."""

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        # Unzip trajectory bundle
        trj_dir: str = fu.create_unique_dir()
        trj_list: list[str] = fu.unzip_list(self.input_trj_zip_path, trj_dir, self.out_log)

        # Copy trajectories to container
        if self.container_path:
            for index, trajectory_file_path in enumerate(trj_list):
                shutil.copy2(trajectory_file_path, self.stage_io_dict.get("unique_dir", ""))
                trj_list[index] = str(Path(self.container_volume_path).joinpath(Path(trajectory_file_path).name))

        # Create command line
        self.cmd = [self.binary_path, 'trjcat',
                    '-f', " ".join(trj_list),
                    '-o', self.stage_io_dict["out"]["output_trj_path"]]

        if self.concatenate:
            self.cmd.append('-cat')
            fu.log('Only concatenate the files without removal of frames with identical timestamps.', self.out_log, self.global_log)

        if self.gmx_lib:
            self.env_vars_dict['GMXLIB'] = self.gmx_lib

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Remove temporal files
        self.tmp_files.extend([
            # self.stage_io_dict.get("unique_dir", ""),
            trj_dir
        ])
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)
        return self.return_code


def trjcat(input_trj_zip_path: str, output_trj_path: str, properties: Optional[dict] = None, **kwargs) -> int:
    """Create :class:`Trjcat <gromacs.trjcat.Trjcat>` class and
    execute the :meth:`launch() <gromacs.trjcat.Trjcat.launch>` method."""

    return Trjcat(input_trj_zip_path=input_trj_zip_path, output_trj_path=output_trj_path,
                  properties=properties, **kwargs).launch()


trjcat.__doc__ = Trjcat.__doc__


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Wrapper of the GROMACS gmx trjcat module.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('-c', '--config', required=False, help="This file can be a YAML file, JSON file or JSON string")

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_trj_zip_path', required=True)
    required_args.add_argument('--output_trj_path', required=True)

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    trjcat(input_trj_zip_path=args.input_trj_zip_path, output_trj_path=args.output_trj_path,
           properties=properties)


if __name__ == '__main__':
    main()
