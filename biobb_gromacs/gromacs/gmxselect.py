#!/usr/bin/env python3

"""Module containing the Select class and the command line interface."""
from typing import Optional
from pathlib import Path
from biobb_common.generic.biobb_object import launcher
from biobb_common.tools import file_utils as fu
from biobb_gromacs.gromacs.common import GromacsBlock


class Gmxselect(GromacsBlock):
    """
    | biobb_gromacs Gmxselect
    | Wrapper of the `GROMACS select <http://manual.gromacs.org/current/onlinehelp/gmx-select.html>`_ module.
    | The GROMACS select module writes out basic data about dynamic selections. It can be used for some simple analyses, or the output can be combined with output from other programs and/or external analysis programs to calculate more complex things.

    Args:
        input_structure_path (str): Path to the input GRO/PDB/TPR file. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/make_ndx.tpr>`_. Accepted formats: pdb (edam:format_1476), gro (edam:format_2033), tpr (edam:format_2333).
        output_ndx_path (str): Path to the output index NDX file. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_select.ndx>`_. Accepted formats: ndx (edam:format_2033).
        input_ndx_path (str) (Optional): Path to the input index NDX file. File type: input. Accepted formats: ndx (edam:format_2033).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **selection** (*str*) - ("a CA C N O") Heavy atoms. Atom selection string.
            * **append** (*bool*) - (False) Append the content of the input_ndx_path to the output_ndx_path.
            * **binary_path** (*str*) - ("gmx") Path to the GROMACS executable binary.
            * **gmx_nobackup** (*bool*) - (True) Add the -nobackup flag: GROMACS overwrites the existing files without backing them up.
            * **gmx_nocopyright** (*bool*) - (True) Add the -nocopyright flag: GROMACS does not print its copyright and citation header.
            * **gmx_lib** (*str*) - (None) Path set GROMACS GMXLIB environment variable.
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

            from biobb_gromacs.gromacs.gmxselect import gmxselect
            prop = { 'selection': '"Mynewgroup" group "Protein-H" and not same residue as within 0.4 of resname ARG' }
            gmxselect(input_structure_path='/path/to/myStructure.gro',
                      output_ndx_path='/path/to/newIndex.ndx',
                      properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS Gmxselect
            * version: 2025.2
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_structure_path: str, output_ndx_path: str, input_ndx_path: Optional[str] = None,
                 properties: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**locals())

    def run(self) -> None:
        """Execute the :class:`Gmxselect <gromacs.gmxselect.Gmxselect>` object."""

        selection_file_path = Path(str(self.stage_io_dict.get("unique_dir", ""))).joinpath("gmxselect_selection.dat")
        with open(selection_file_path, "w") as selection_file:
            selection_file.write(f"{self.selection}\n")

        self.cmd = [self.binary_path, 'select',
                    '-s', self.stage_io_dict["in"]["input_structure_path"],
                    '-on', self.stage_io_dict["out"]["output_ndx_path"]
                    ]

        # Check the host path: with containers stage_io_dict holds the path inside the container
        if bool(self.io_dict["in"].get("input_ndx_path")) and Path(self.io_dict["in"]["input_ndx_path"]).exists():
            self.cmd.append('-n')
            self.cmd.append(self.stage_io_dict["in"].get("input_ndx_path"))

        self.cmd.append('-sf')
        self.cmd.append(self.staged_path(selection_file_path))

        # Run Biobb block
        self.run_biobb()

        # Remove temporal files
        self.tmp_files.append(str(selection_file_path))

        # With the append property, append the input index file to the output index file.
        if self.io_dict["in"].get("input_ndx_path"):
            if self.append:
                fu.log(f"Appending {self.io_dict['in'].get('input_ndx_path')} to {self.io_dict['out']['output_ndx_path']}", self.out_log, self.global_log)
                # The output is replaced, not appended to: Docker can have written it as root
                output_ndx = Path(self.sandbox_file("output_ndx_path"))
                content = output_ndx.read_text()
                output_ndx.unlink()
                with open(output_ndx, 'w') as out_ndx_file:
                    out_ndx_file.write(content + '\n')
                    with open(self.io_dict["in"].get("input_ndx_path", '')) as in_ndx_file:
                        for line in in_ndx_file:
                            out_ndx_file.write(line)


gmxselect = launcher(Gmxselect)


if __name__ == '__main__':
    Gmxselect.main()
