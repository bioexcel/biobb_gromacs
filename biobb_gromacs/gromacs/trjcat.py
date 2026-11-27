#!/usr/bin/env python3

"""Module containing the Trjcat class and the command line interface."""
from typing import Optional
from biobb_common.generic.biobb_object import launcher
from biobb_common.tools import file_utils as fu
from biobb_gromacs.gromacs.common import GromacsBlock


class Trjcat(GromacsBlock):
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
            * **gmx_nobackup** (*bool*) - (True) Add the -nobackup flag: GROMACS overwrites the existing files without backing them up.
            * **gmx_nocopyright** (*bool*) - (True) Add the -nocopyright flag: GROMACS does not print its copyright and citation header.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.
            * **container_path** (*str*) - (None)  Path to the binary executable of your container.
            * **container_image** (*str*) - (None) Container Image identifier.
            * **container_volume_path** (*str*) - ("/data") Path to an internal directory in the container.
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
            * version: 2025.2
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_trj_zip_path: str, output_trj_path: str, properties: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**locals())

        # Should not be copied inside container
        self.input_trj_zip_path = self.io_dict["in"].pop("input_trj_zip_path")

    def run(self) -> None:
        """Execute the :class:`Trjcat <gromacs.trjcat.Trjcat>` object."""

        # Unzip the trajectory bundle in the sandbox
        trj_list: list[str] = fu.unzip_list(self.input_trj_zip_path, self.stage_io_dict.get("unique_dir", ""), self.out_log)
        trj_list = [self.staged_path(p) for p in trj_list]

        # Create command line
        self.cmd = [self.binary_path, 'trjcat',
                    '-f', " ".join(trj_list),
                    '-o', self.stage_io_dict["out"]["output_trj_path"]]

        if self.concatenate:
            self.cmd.append('-cat')
            fu.log('Only concatenate the files without removal of frames with identical timestamps.', self.out_log, self.global_log)

        # Run Biobb block
        self.run_biobb()


trjcat = launcher(Trjcat)


if __name__ == '__main__':
    Trjcat.main()
