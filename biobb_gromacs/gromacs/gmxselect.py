#!/usr/bin/env python3

"""Module containing the Select class and the command line interface."""
import argparse
from typing import Optional
from pathlib import Path
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_gromacs.gromacs.common import get_gromacs_version


class Gmxselect(BiobbObject):
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
            * **gmx_lib** (*str*) - (None) Path set GROMACS GMXLIB environment variable.
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

            from biobb_gromacs.gromacs.gmxselect import gmxselect
            prop = { 'selection': '"Mynewgroup" group "Protein-H" and not same residue as within 0.4 of resname ARG' }
            gmxselect(input_structure_path='/path/to/myStructure.gro',
                      output_ndx_path='/path/to/newIndex.ndx',
                      properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS Gmxselect
            * version: 2024.5
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_structure_path: str, output_ndx_path: str, input_ndx_path: Optional[str] = None,
                 properties: Optional[dict] = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_structure_path": input_structure_path, "input_ndx_path": input_ndx_path},
            "out": {"output_ndx_path": output_ndx_path}
        }

        # Properties specific for BB
        self.selection = properties.get('selection', "a CA C N O")
        self.append = properties.get('append', False)

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
        """Execute the :class:`Gmxselect <gromacs.gmxselect.Gmxselect>` object."""

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        self.cmd = [self.binary_path, 'select',
                    '-s', self.stage_io_dict["in"]["input_structure_path"],
                    '-on', self.stage_io_dict["out"]["output_ndx_path"]
                    ]

        if self.stage_io_dict["in"].get("input_ndx_path") and Path(
                self.stage_io_dict["in"].get("input_ndx_path")).exists():
            self.cmd.append('-n')
            self.cmd.append(self.stage_io_dict["in"].get("input_ndx_path"))

        self.cmd.append('-select')
        self.cmd.append("\'"+self.selection+"\'")

        if self.gmx_lib:
            self.env_vars_dict['GMXLIB'] = self.gmx_lib

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        if self.io_dict["in"].get("input_ndx_path"):
            if self.append:
                fu.log(f"Appending {self.io_dict['in'].get('input_ndx_path')} to {self.io_dict['out']['output_ndx_path']}", self.out_log, self.global_log)
                with open(self.io_dict["out"]["output_ndx_path"], 'a') as out_ndx_file:
                    out_ndx_file.write('\n')
                    with open(self.io_dict["in"].get("input_ndx_path", '')) as in_ndx_file:
                        for line in in_ndx_file:
                            out_ndx_file.write(line)

        # Remove temporal files
        # self.tmp_files.append(self.stage_io_dict.get("unique_dir", ''))
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)
        return self.return_code


def gmxselect(input_structure_path: str, output_ndx_path: str,
              input_ndx_path: Optional[str] = None, properties: Optional[dict] = None,
              **kwargs) -> int:
    """Create :class:`Gmxselect <gromacs.gmxselect.Gmxselect>` class and
    execute the :meth:`launch() <gromacs.gmxselect.Gmxselect.launch>` method."""
    return Gmxselect(input_structure_path=input_structure_path,
                     output_ndx_path=output_ndx_path,
                     input_ndx_path=input_ndx_path,
                     properties=properties, **kwargs).launch()


    gmxselect.__doc__ = Gmxselect.__doc__


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Wrapper for the GROMACS select module.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('-c', '--config', required=False, help="This file can be a YAML file, JSON file or JSON string")

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_structure_path', required=True)
    required_args.add_argument('--output_ndx_path', required=True)
    parser.add_argument('--input_ndx_path', required=False)

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    gmxselect(input_structure_path=args.input_structure_path,
              output_ndx_path=args.output_ndx_path,
              input_ndx_path=args.input_ndx_path,
              properties=properties)


if __name__ == '__main__':
    main()
