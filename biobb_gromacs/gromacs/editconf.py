#!/usr/bin/env python3

"""Module containing the Editconf class and the command line interface."""

import argparse
from typing import Optional

from biobb_common.configuration import settings
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger

from biobb_gromacs.gromacs.common import get_gromacs_version


class Editconf(BiobbObject):
    """
    | biobb_gromacs Editconf
    | Wrapper class for the `GROMACS editconf <http://manual.gromacs.org/current/onlinehelp/gmx-editconf.html>`_ module.
    | The GROMACS solvate module generates a box around the selected structure.

    Args:
        input_gro_path (str): Path to the input GRO file. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/editconf.gro>`_. Accepted formats: gro (edam:format_2033), pdb (edam:format_1476).
        output_gro_path (str): Path to the output GRO file. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_editconf.gro>`_. Accepted formats: pdb (edam:format_1476), gro (edam:format_2033).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **distance_to_molecule** (*float*) - (1.0) [0~100|0.1] Distance of the box from the outermost atom in nm. ie 1.0nm = 10 Angstroms.
            * **box_vector_lenghts** (*str*) - (None) Array of floats defining the box vector lenghts ie "0.5 0.5 0.5". If this option is used the distance_to_molecule property will be ignored.
            * **box_type** (*str*) - ("cubic") Geometrical shape of the solvent box. Values: cubic (rectangular box with all sides equal), triclinic (triclinic box), dodecahedron (rhombic dodecahedron), octahedron (truncated octahedron).
            * **center_molecule** (*bool*) - (True) Center molecule in the box.
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

            from biobb_gromacs.gromacs.editconf import editconf
            prop = { 'distance_to_molecule': 1.0,
                     'box_type': 'cubic'}
            editconf(input_gro_path='/path/to/structure.gro',
                     output_gro_path='/path/to/newStructure.gro',
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

    def __init__(
        self,
        input_gro_path: str,
        output_gro_path: str,
        properties: Optional[dict] = None,
        **kwargs,
    ) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_gro_path": input_gro_path},
            "out": {"output_gro_path": output_gro_path},
        }

        # Properties specific for BB
        self.distance_to_molecule = properties.get("distance_to_molecule", 1.0)
        self.box_vector_lenghts = properties.get("box_vector_lenghts")
        self.box_type = properties.get("box_type", "cubic")
        self.center_molecule = properties.get("center_molecule", True)

        # Properties common in all GROMACS BB
        self.gmx_lib = properties.get("gmx_lib", None)
        self.binary_path: str = properties.get("binary_path", "gmx")
        self.gmx_nobackup = properties.get("gmx_nobackup", True)
        self.gmx_nocopyright = properties.get("gmx_nocopyright", True)
        if self.gmx_nobackup:
            self.binary_path += " -nobackup"
        if self.gmx_nocopyright:
            self.binary_path += " -nocopyright"
        if not self.container_path:
            self.gmx_version = get_gromacs_version(self.binary_path)

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Editconf <gromacs.editconf.Editconf>` object."""

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        # Create command line
        self.cmd = [
            self.binary_path,
            "editconf",
            "-f",
            self.stage_io_dict["in"]["input_gro_path"],
            "-o",
            self.stage_io_dict["out"]["output_gro_path"],
            "-bt",
            self.box_type,
        ]

        if self.box_vector_lenghts:
            if not isinstance(self.box_vector_lenghts, str):
                self.box_vector_lenghts = " ".join(map(str, self.box_vector_lenghts))
            self.cmd.append("-box")
            self.cmd.append(self.box_vector_lenghts)
        else:
            self.cmd.append("-d")
            self.cmd.append(str(self.distance_to_molecule))
            fu.log(
                "Distance of the box to molecule: %6.2f" % self.distance_to_molecule,
                self.out_log,
                self.global_log,
            )

        if self.center_molecule:
            self.cmd.append("-c")
            fu.log("Centering molecule in the box.", self.out_log, self.global_log)

        fu.log("Box type: %s" % self.box_type, self.out_log, self.global_log)

        if self.gmx_lib:
            self.env_vars_dict = self.gmx_lib

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Remove temporal files
        # self.tmp_files.append(str(self.stage_io_dict.get("unique_dir", "")))
        self.remove_tmp_files()

        # self.check_arguments(output_files_created=True, raise_exception=False)
        return self.return_code


def editconf(
    input_gro_path: str,
    output_gro_path: str,
    properties: Optional[dict] = None,
    **kwargs,
) -> int:
    """Create :class:`Editconf <gromacs.editconf.Editconf>` class and
    execute the :meth:`launch() <gromacs.editconf.Editconf.launch>` method."""

    return Editconf(
        input_gro_path=input_gro_path,
        output_gro_path=output_gro_path,
        properties=properties,
        **kwargs,
    ).launch()


editconf.__doc__ = Editconf.__doc__


def main():
    parser = argparse.ArgumentParser(
        description="Wrapper of the GROMACS gmx editconf module.",
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
    required_args.add_argument("--input_gro_path", required=True)
    required_args.add_argument("--output_gro_path", required=True)

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    editconf(
        input_gro_path=args.input_gro_path,
        output_gro_path=args.output_gro_path,
        properties=properties,
    )


if __name__ == "__main__":
    main()
