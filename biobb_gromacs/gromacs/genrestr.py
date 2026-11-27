#!/usr/bin/env python3

"""Module containing the Genrestr class and the command line interface."""

from pathlib import Path
from typing import Optional, Union

from biobb_common.generic.biobb_object import launcher
from biobb_common.tools import file_utils as fu

from biobb_gromacs.gromacs.common import GromacsBlock


class Genrestr(GromacsBlock):
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

            from biobb_gromacs.gromacs.genrestr import genrestr
            prop = { 'restrained_group': 'system',
                     'force_constants': '500 500 500' }
            genrestr(input_structure_path='/path/to/myStructure.gro',
                     output_itp_path='/path/to/newTopologyAddOn.itp',
                     properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS Genrestr
            * version: 2025.2
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
        super().__init__(**locals())

        # Properties specific for BB
        self.force_constants = str(self.force_constants)

    def prepare(self) -> None:
        """Create the stdin file with the restrained group."""
        self.io_dict["in"]["stdin_file_path"] = fu.create_stdin_file(f"{self.restrained_group}")

    def run(self) -> None:
        """Execute the :class:`Grompp <gromacs.grompp.Grompp>` object."""

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

        # Run Biobb block
        self.run_biobb()

        # Remove temporal files
        self.tmp_files.append(str(self.io_dict["in"].get("stdin_file_path")))


genrestr = launcher(Genrestr)


if __name__ == "__main__":
    Genrestr.main()
