#!/usr/bin/env python3

"""Module containing the Convert_tpr class and the command line interface."""
from pathlib import Path
from typing import Optional
from biobb_common.generic.biobb_object import launcher
from biobb_common.tools import file_utils as fu
from biobb_gromacs.gromacs.common import GromacsBlock


class ConvertTpr(GromacsBlock):
    """
    | biobb_gromacs ConvertTpr
    | Wrapper of the `GROMACS convert-tpr <https://manual.gromacs.org/current/onlinehelp/gmx-convert-tpr.html>`_ module.
    | The GROMACS convert-tpr module can edit run input files (.tpr): modify the run length (extend/until/nsteps) or trim the tpr file to a subset of atoms defined in an index file (input_ndx_path). Note that GROMACS does not allow both operations in a single call, so when an index file is provided the extend/until/nsteps properties are ignored.

    Args:
        input_tpr_path (str): Path to the input portable binary run file TPR. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_grompp.tpr>`_. Accepted formats: tpr (edam:format_2333).
        output_tpr_path (str): Path to the output portable binary run file TPR. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_grompp.tpr>`_. Accepted formats: tpr (edam:format_2333).
        input_ndx_path (str) (Optional): Path to the input index NDX file, used to trim the tpr file to a subset of atoms. File type: input. Accepted formats: ndx (edam:format_2033).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **extend** (*int*) - (None) Extend the runtime by this amount (ps).
            * **until** (*int*) - (None) Extend the runtime until this ending time (ps).
            * **nsteps** (*int*) - (None) Change the number of steps remaining to be made.
            * **output_group** (*str*) - ("System") Index group to write to the output tpr file when trimming to a subset of atoms. Only used when input_ndx_path is provided.
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

            from biobb_gromacs.gromacs.convert_tpr import convert_tpr

            prop = { 'extend': 100000}
            convert_tpr(input_tpr_path='/path/to/myStructure.tpr',
                   output_tpr_path='/path/to/newCompiledBin.tpr',
                   properties=prop)

            # Trim the tpr file to a subset of atoms defined in an index file
            prop = { 'output_group': 'Protein'}
            convert_tpr(input_tpr_path='/path/to/myStructure.tpr',
                   output_tpr_path='/path/to/trimmedBin.tpr',
                   input_ndx_path='/path/to/myIndex.ndx',
                   properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS Convert-tpr
            * version: 2025.2
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_tpr_path: str, output_tpr_path: str,
                 input_ndx_path: Optional[str] = None,
                 properties: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**locals())

    def prepare(self) -> None:
        """Create the stdin file with the output group."""
        # When trimming to a subset (an index file is provided), GROMACS
        # convert-tpr prompts for the output group; answer it via stdin.
        if self.io_dict["in"].get("input_ndx_path"):
            self.io_dict["in"]["stdin_file_path"] = fu.create_stdin_file(f"{self.output_group}")

    def run(self) -> None:
        """Execute the :class:`ConvertTpr <gromacs.convert_tpr.ConvertTpr>` object."""

        self.cmd = [self.binary_path, 'convert-tpr',
                    '-s', self.stage_io_dict["in"]["input_tpr_path"],
                    '-o', self.stage_io_dict["out"]["output_tpr_path"]
                    ]

        # Check the host path: with containers stage_io_dict holds the path inside the container
        trimming = bool(self.io_dict["in"].get("input_ndx_path")) and Path(self.io_dict["in"]["input_ndx_path"]).exists()

        if trimming:
            # Trim the tpr to the selected index group. GROMACS does not allow
            # combining index-group extraction with runtime modification
            # (-extend/-until/-nsteps) in a single convert-tpr call.
            self.cmd.append('-n')
            self.cmd.append(self.stage_io_dict["in"].get("input_ndx_path"))
            if self.extend or self.until or self.nsteps:
                fu.log("Warning: extend, until and nsteps are ignored when trimming the tpr "
                       "file to an index group; GROMACS convert-tpr cannot do both in a single call.",
                       self.out_log, self.global_log)
        else:
            if self.extend:
                self.cmd.extend(['-extend', str(self.extend)])
            if self.until:
                self.cmd.extend(['-until', str(self.until)])
            if self.nsteps:
                self.cmd.extend(['-nsteps', str(self.nsteps)])

        # Add stdin input file to answer the output group prompt when trimming
        if self.io_dict["in"].get("stdin_file_path"):
            self.cmd.append('<')
            self.cmd.append(self.stage_io_dict["in"]["stdin_file_path"])

        # Run Biobb block
        self.run_biobb()

        if self.io_dict["in"].get("stdin_file_path"):
            self.tmp_files.append(str(self.io_dict["in"].get("stdin_file_path")))


convert_tpr = launcher(ConvertTpr)


if __name__ == '__main__':
    ConvertTpr.main()
