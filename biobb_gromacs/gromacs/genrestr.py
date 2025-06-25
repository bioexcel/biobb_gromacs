#!/usr/bin/env python3

"""Module containing the Genrestr class and the command line interface."""

import argparse
from pathlib import Path
from typing import Optional, Union

from biobb_common.configuration import settings
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger

from biobb_gromacs.gromacs.common import get_gromacs_version


class Genrestr(BiobbObject):
    """
    | biobb_gromacs Genrestr
    | Wrapper of the `GROMACS genrestr <http://manual.gromacs.org/current/onlinehelp/gmx-genrestr.html>`_ module.
    | The GROMACS genrestr module, produces an #include file for a topology containing a list of atom numbers and three force constants for the x-, y-, and z-direction based on the contents of the -f file. A single isotropic force constant may be given on the command line instead of three components.

    Args:
        input_structure_path (str): Path to the input structure PDB, GRO or TPR format. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/genrestr.gro>`_. Accepted formats: pdb (edam:format_1476), gro (edam:format_2033), tpr (edam:format_2333).
        output_itp_path (str): Path the output ITP topology file with restrains. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_genrestr.itp>`_. Accepted formats: itp (edam:format_3883).
        input_ndx_path (str) (Optional): Path to the input GROMACS index file, NDX format. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/genrestr.ndx>`_. Accepted formats: ndx (edam:format_2033).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **restrained_group** (*str*) - ("system") Index group that will be restrained.
            * **force_constants** (*str*) - ("500 500 500") Array of three floats defining the force constants
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

            from biobb_gromacs.gromacs.genrestr import genrestr
            prop = { 'restrained_group': 'system',
                     'force_constants': '500 500 500' }
            genrestr(input_structure_path='/path/to/myStructure.gro',
                     output_itp_path='/path/to/newTopologyAddOn.itp',
                     properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS Genrestr
            * version: 2024.5
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(
        self,
        input_structure_path: Union[str, Path],
        output_itp_path: Union[str, Path],
        input_ndx_path: Optional[Union[str, Path]] = None,
        properties: Optional[dict] = None,
        **kwargs,
    ) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {
                "input_structure_path": input_structure_path,
                "input_ndx_path": input_ndx_path,
            },
            "out": {"output_itp_path": output_itp_path},
        }

        # Properties specific for BB
        self.force_constants = str(properties.get("force_constants", "500 500 500"))
        self.restrained_group = properties.get("restrained_group", "system")

        # Properties common in all GROMACS BB
        self.gmx_lib = properties.get("gmx_lib", None)
        self.binary_path = properties.get("binary_path", "gmx")
        self.gmx_nobackup = properties.get("gmx_nobackup", True)
        self.gmx_nocopyright = properties.get("gmx_nocopyright", True)
        if self.gmx_nobackup:
            self.binary_path = f"{self.binary_path}  -nobackup"
        if self.gmx_nocopyright:
            self.binary_path = f"{self.binary_path} -nocopyright"
        if not self.container_path:
            self.gmx_version = get_gromacs_version(str(self.binary_path))

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Grompp <gromacs.grompp.Grompp>` object."""

        # Setup Biobb
        if self.check_restart():
            return 0

        self.io_dict["in"]["stdin_file_path"] = fu.create_stdin_file(
            f"{self.restrained_group}"
        )
        self.stage_files()

        self.cmd = [
            str(self.binary_path),
            "genrestr",
            "-f",
            self.stage_io_dict["in"]["input_structure_path"],
            "-o",
            self.stage_io_dict["out"]["output_itp_path"],
        ]

        if not isinstance(self.force_constants, str):
            self.force_constants = " ".join(map(str, self.force_constants))

        self.cmd.append("-fc")
        self.cmd.append(self.force_constants)

        if self.stage_io_dict["in"].get("input_ndx_path"):
            self.cmd.append("-n")
            self.cmd.append(self.stage_io_dict["in"]["input_ndx_path"])

        # Add stdin input file
        self.cmd.append("<")
        self.cmd.append(self.stage_io_dict["in"]["stdin_file_path"])

        if self.gmx_lib:
            self.env_vars_dict["GMXLIB"] = self.gmx_lib

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Remove temporal files
        self.tmp_files.extend(
            [
                # str(self.stage_io_dict.get("unique_dir", "")),
                str(self.io_dict["in"].get("stdin_file_path")),
            ]
        )
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)
        return self.return_code


def genrestr(
    input_structure_path: Union[str, Path],
    output_itp_path: Union[str, Path],
    input_ndx_path: Optional[Union[str, Path]] = None,
    properties: Optional[dict] = None,
    **kwargs,
) -> int:
    """Create :class:`Genrestr <gromacs.genrestr.Genrestr>` class and
    execute the :meth:`launch() <gromacs.genrestr.Genrestr.launch>` method."""

    return Genrestr(
        input_structure_path=input_structure_path,
        output_itp_path=output_itp_path,
        input_ndx_path=input_ndx_path,
        properties=properties,
        **kwargs,
    ).launch()


genrestr.__doc__ = Genrestr.__doc__


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(
        description="Wrapper for the GROMACS genion module.",
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
    )
    parser.add_argument(
        "-c",
        "--config",
        required=False,
        help="This file can be a YAML file, JSON file or JSON string",
    )

    # Specific args of each building block
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("--input_structure_path", required=True)
    required_args.add_argument("--output_itp_path", required=True)
    parser.add_argument("--input_ndx_path", required=False)

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    genrestr(
        input_structure_path=args.input_structure_path,
        input_ndx_path=args.input_ndx_path,
        output_itp_path=args.output_itp_path,
        properties=properties,
    )


if __name__ == "__main__":
    main()
