#!/usr/bin/env python3

"""Module containing the Pdb2gmx class and the command line interface."""
import os
import argparse
from typing import Optional
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_gromacs.gromacs.common import get_gromacs_version


class Pdb2gmx(BiobbObject):
    """
    | biobb_gromacs Pdb2gmx
    | Wrapper class for the `GROMACS pdb2gmx <http://manual.gromacs.org/current/onlinehelp/gmx-pdb2gmx.html>`_ module.
    | The GROMACS pdb2gmx module, reads a .pdb (or .gro) file, reads some database files, adds hydrogens to the molecules and generates coordinates in GROMACS (GROMOS), or optionally .pdb, format and a topology in GROMACS format. These files can subsequently be processed to generate a run input file.

    Args:
        input_pdb_path (str): Path to the input PDB file. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/egfr.pdb>`_. Accepted formats: pdb (edam:format_1476).
        output_gro_path (str): Path to the output GRO file. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_pdb2gmx.gro>`_. Accepted formats: gro (edam:format_2033).
        output_top_zip_path (str): Path the output TOP topology in zip format. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_pdb2gmx.zip>`_. Accepted formats: zip (edam:format_3987).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **water_type** (*str*) - ("spce") Water molecule type. Values: spc, spce, tip3p, tip4p, tip5p, tips3p.
            * **force_field** (*str*) - ("amber99sb-ildn") Force field to be used during the conversion.  Values: gromos45a3, charmm27, gromos53a6, amber96, amber99, gromos43a2, gromos54a7, gromos43a1, amberGS, gromos53a5, amber99sb, amber03, amber99sb-ildn, oplsaa, amber94, amber99sb-star-ildn-mut.
            * **ignh** (*bool*) - (False) Should pdb2gmx ignore the hidrogens in the original structure.
            * **lys** (*list*) - (None) Lysine protonation states for each chain in the input pdb. Each item of the list should be a string with the protonation states for that chain or empty if the residue is not present in that chain (0: not protonated, 1: protonated).
            * **arg** (*list*) - (None) Arginine protonation states for each chain in the input pdb. Each item of the list should be a string with the protonation states for that chain or empty if the residue is not present in that chain (0: not protonated, 1: protonated).
            * **asp** (*list*) - (None) Aspartic acid protonation states for each chain in the input pdb. Each item of the list should be a string with the protonation states for that chain or empty if the residue is not present in that chain (0: not protonated, 1: protonated).
            * **glu** (*list*) - (None) Glutamic acid protonation states for each chain in the input pdb. Each item of the list should be a string with the protonation states for that chain or empty if the residue is not present in that chain (0: not protonated, 1: protonated).
            * **gln** (*list*) - (None) Glutamine protonation states for each chain in the input pdb. Each item of the list should be a string with the protonation states for that chain or empty if the residue is not present in that chain (0: not protonated, 1: protonated).
            * **his** (*list*) - (None) Histidine protonation states for each chain in the input pdb. Each item of the list should be a string with the protonation states for that chain or empty if the residue is not present in that chain. Make sure residues are named HIS (0: HID, 1: HIE, 2: HIP, 3: HIS1).
            * **merge** (*bool*) - (False) Merge all chains into a single molecule.
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

            from biobb_gromacs.gromacs.pdb2gmx import pdb2gmx
            prop = { 'his': ['0 0 1 1 0 0 0', '1 1 0 1'] }
            pdb2gmx(input_pdb_path='/path/to/myStructure.pdb',
                    output_gro_path='/path/to/newStructure.gro',
                    output_top_zip_path='/path/to/newTopology.zip',
                    properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS Pdb2gmx
            * version: 2024.5
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_pdb_path: str, output_gro_path: str, output_top_zip_path: str, properties: Optional[dict] = None,
                 **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_pdb_path": input_pdb_path},
            "out": {"output_gro_path": output_gro_path, "output_top_zip_path": output_top_zip_path}
        }

        # Properties specific for BB
        self.internal_top_name = properties.get('internal_top_name', 'p2g.top')  # Excluded from documentation for simplicity
        self.internal_itp_name = properties.get('internal_itp_name', 'posre.itp')  # Excluded from documentation for simplicity
        self.water_type = properties.get('water_type', 'spce')
        self.force_field = properties.get('force_field', 'amber99sb-ildn')
        self.ignh = properties.get('ignh', False)
        self.lys = properties.get('lys', None)
        self.arg = properties.get('arg', None)
        self.asp = properties.get('asp', None)
        self.glu = properties.get('glu', None)
        self.gln = properties.get('gln', None)
        self.his = properties.get('his', None)
        self.merge = properties.get('merge', False)

        # Properties common in all GROMACS BB
        self.gmx_lib = properties.get('gmx_lib', None)
        self.binary_path: str = properties.get('binary_path', 'gmx')
        self.gmx_nobackup = properties.get('gmx_nobackup', True)
        self.gmx_nocopyright = properties.get('gmx_nocopyright', True)
        if self.gmx_nobackup:
            self.binary_path += ' -nobackup'
        if self.gmx_nocopyright:
            self.binary_path += ' -nocopyright'
        if not self.container_path:
            self.gmx_version = get_gromacs_version(self.binary_path)

        # Support string for single chain
        if isinstance(self.lys, str):
            self.lys = [self.lys]
        if isinstance(self.arg, str):
            self.arg = [self.arg]
        if isinstance(self.asp, str):
            self.asp = [self.asp]
        if isinstance(self.glu, str):
            self.glu = [self.glu]
        if isinstance(self.gln, str):
            self.gln = [self.gln]
        if isinstance(self.his, str):
            self.his = [self.his]

        # Make sure all have the same length
        self.check_lengths(self.lys, self.arg, self.asp, self.glu, self.gln, self.his)

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Pdb2gmx <gromacs.pdb2gmx.Pdb2gmx>` object."""

        # Setup Biobb
        if self.check_restart():
            return 0

        # Create stdin file if needed
        stdin_content = ''
        num_chains = self.find_length(self.lys, self.arg, self.asp, self.glu, self.gln, self.his)
        for i in range(num_chains):
            if self.lys is not None:
                stdin_content += f' {self.lys[i]}'
            if self.arg is not None:
                stdin_content += f' {self.arg[i]}'
            if self.asp is not None:
                stdin_content += f' {self.asp[i]}'
            if self.glu is not None:
                stdin_content += f' {self.glu[i]}'
            if self.gln is not None:
                stdin_content += f' {self.gln[i]}'
            if self.his is not None:
                stdin_content += f' {self.his[i]}'

        if stdin_content:
            self.io_dict['in']['stdin_file_path'] = fu.create_stdin_file(stdin_content)
        self.stage_files()

        internal_top_name = fu.create_name(prefix=self.prefix, step=self.step, name=self.internal_top_name)
        internal_itp_name = fu.create_name(prefix=self.prefix, step=self.step, name=self.internal_itp_name)

        # Create command line
        self.cmd = [self.binary_path, "pdb2gmx",
                    "-f", self.stage_io_dict["in"]["input_pdb_path"],
                    "-o", self.stage_io_dict["out"]["output_gro_path"],
                    "-p", internal_top_name,
                    "-water", self.water_type,
                    "-ff", self.force_field,
                    "-i", internal_itp_name]

        if self.ignh:
            self.cmd.append("-ignh")
        if self.merge:
            self.cmd.append("-merge")
            self.cmd.append("all")
        if self.lys:
            self.cmd.append("-lys")
        if self.arg:
            self.cmd.append("-arg")
        if self.asp:
            self.cmd.append("-asp")
        if self.glu:
            self.cmd.append("-glu")
        if self.gln:
            self.cmd.append("-gln")
        if self.his:
            self.cmd.append("-his")

        if stdin_content:
            self.cmd.append('<')
            self.cmd.append(self.stage_io_dict["in"]["stdin_file_path"])

        if self.gmx_lib:
            self.env_vars_dict['GMXLIB'] = self.gmx_lib

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        if self.container_path:
            internal_top_name = os.path.join(self.stage_io_dict.get("unique_dir", ""), internal_top_name)

        # zip topology
        fu.log('Compressing topology to: %s' % self.io_dict["out"]["output_top_zip_path"], self.out_log,
               self.global_log)
        fu.zip_top(zip_file=self.io_dict["out"]["output_top_zip_path"], top_file=internal_top_name, out_log=self.out_log, remove_original_files=self.remove_tmp)

        # Remove temporal files
        self.tmp_files.extend([
            self.internal_top_name,
            self.internal_itp_name,
            self.io_dict['in'].get("stdin_file_path", "")
        ])
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)
        return self.return_code

    def check_lengths(self, *lists):
        """
        Make sure all lists are the same length
        """
        # Find length of each list
        lengths = [len(lst) for lst in lists if lst is not None]

        # Check if all lengths are the same
        all_equal = True
        if len(lengths) > 0:
            all_equal = len(set(lengths)) == 1

        if not all_equal:
            raise ValueError(f"""All protonation arrays (lys, arg, asp, glu, gln, his) must have the same length
                             (one string per chain and empty string if residue is not present in that chain). Found lengths: {lengths}""")

    def find_length(self, *lists) -> int:
        """
        Find length of the first list
        """
        # Find length of each list
        lengths = [len(lst) for lst in lists if lst is not None]

        # Return the length of the first list, if any
        if len(lengths) > 0:
            return lengths[0]
        else:
            return 0


def pdb2gmx(input_pdb_path: str, output_gro_path: str, output_top_zip_path: str,
            properties: Optional[dict] = None, **kwargs) -> int:
    """Create :class:`Pdb2gmx <gromacs.pdb2gmx.Pdb2gmx>` class and
    execute the :meth:`launch() <gromacs.pdb2gmx.Pdb2gmx.launch>` method."""

    return Pdb2gmx(input_pdb_path=input_pdb_path, output_gro_path=output_gro_path,
                   output_top_zip_path=output_top_zip_path, properties=properties,
                   **kwargs).launch()


pdb2gmx.__doc__ = Pdb2gmx.__doc__


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Wrapper of the GROMACS pdb2gmx module.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('-c', '--config', required=False, help="This file can be a YAML file, JSON file or JSON string")

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_pdb_path', required=True)
    required_args.add_argument('--output_gro_path', required=True)
    required_args.add_argument('--output_top_zip_path', required=True)

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    pdb2gmx(input_pdb_path=args.input_pdb_path, output_gro_path=args.output_gro_path,
            output_top_zip_path=args.output_top_zip_path, properties=properties)


if __name__ == '__main__':
    main()
