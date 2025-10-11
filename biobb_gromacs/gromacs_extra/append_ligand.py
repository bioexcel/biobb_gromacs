#!/usr/bin/env python3

"""Module containing the AppendLigand class and the command line interface."""

import argparse
import re
import shutil
from pathlib import Path
from typing import Optional

from biobb_common.configuration import settings
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger


class AppendLigand(BiobbObject):
    """
    | biobb_gromacs AppendLigand
    | This class takes a ligand ITP file and inserts it in a topology.
    | This module automatizes the process of inserting a ligand ITP file in a GROMACS topology.

    Args:
        input_top_zip_path (str): Path the input topology TOP and ITP files zipball. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs_extra/ndx2resttop.zip>`_. Accepted formats: zip (edam:format_3987).
        input_itp_path (str): Path to the ligand ITP file to be inserted in the topology. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs_extra/pep_ligand.itp>`_. Accepted formats: itp (edam:format_3883).
        output_top_zip_path (str): Path/Name the output topology TOP and ITP files zipball. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs_extra/ref_appendligand.zip>`_. Accepted formats: zip (edam:format_3987).
        input_posres_itp_path (str) (Optional): Path to the position restriction ITP file. File type: input. Accepted formats: itp (edam:format_3883).
        properties (dic):
            * **posres_name** (*str*) - ("POSRES_LIGAND") String to be included in the ifdef clause.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_gromacs.gromacs_extra.append_ligand import append_ligand
            prop = { 'posres_name': 'POSRES_LIGAND' }
            append_ligand(input_top_zip_path='/path/to/myTopology.zip',
                          input_itp_path='/path/to/myTopologyAddOn.itp',
                          output_top_zip_path='/path/to/newTopology.zip',
                          properties=prop)

    Info:
        * wrapped_software:
            * name: In house
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(
        self,
        input_top_zip_path: str,
        input_itp_path: str,
        output_top_zip_path: str,
        input_posres_itp_path: Optional[str] = None,
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
                "input_top_zip_path": input_top_zip_path,
                "input_itp_path": input_itp_path,
                "input_posres_itp_path": input_posres_itp_path,
            },
            "out": {"output_top_zip_path": output_top_zip_path},
        }

        # Properties specific for BB
        self.posres_name = properties.get("posres_name", "POSRES_LIGAND")

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`AppendLigand <gromacs_extra.append_ligand.AppendLigand>` object."""
        # Setup Biobb
        if self.check_restart():
            return 0

        # Unzip topology
        top_file = fu.unzip_top(
            zip_file=str(self.io_dict["in"].get("input_top_zip_path")),
            out_log=self.out_log,
        )
        top_dir = str(Path(top_file).parent)
        itp_name = str(Path(str(self.io_dict["in"].get("input_itp_path"))).name)

        with open(top_file) as top_f:
            top_lines = top_f.readlines()
            top_f.close()
        fu.rm(top_file)

        forcefield_pattern = r"#include.*forcefield.itp\""
        if top_lines:
            for ff_index, line in enumerate(top_lines):
                if re.search(forcefield_pattern, line):
                    break
        else:
            fu.log(
                f'FATAL: Input topfile {top_file} from input_top_zip_path {self.io_dict["in"].get("input_top_zip_path")} is empty.',
                self.out_log,
                self.global_log,
            )
            return 1

        ligand_itp_path = self.io_dict["in"].get("input_itp_path")

        # Read ligand itp contents
        with open(ligand_itp_path, 'r') as itp_file:
            ligand_itp_contents = itp_file.readlines()

        # Separate ligand [ atomtypes ] section from the rest
        lig_atomtypes_section = []
        remaining_itp_contents = []
        in_atomtypes_section = False
        for line in ligand_itp_contents:
            if line.strip().startswith("[ atomtypes ]"):
                in_atomtypes_section = True
                lig_atomtypes_section.append(line)
            elif in_atomtypes_section:
                if line.strip() == "" or line.startswith("["):
                    in_atomtypes_section = False
                    remaining_itp_contents.append(line)
                else:
                    lig_atomtypes_section.append(line)
            else:
                remaining_itp_contents.append(line)

        # If the ligand itp contains an [ atomtypes ] section, merge it into the main topology
        if lig_atomtypes_section:

            # Look for the [ atomtypes ] section in the main topology
            top_atomtypes_section = []
            in_atomtypes_section = False
            for line in top_lines:
                if line.strip().startswith("[ atomtypes ]"):
                    in_atomtypes_section = True
                    top_atomtypes_section.append(line)
                elif in_atomtypes_section:
                    if line.strip() == "" or line.startswith("["):
                        in_atomtypes_section = False
                    else:
                        top_atomtypes_section.append(line)

            # If there is already an [ atomtypes ] section in the main topology
            if top_atomtypes_section:

                # Remove the header and comments of the ligand [ atomtypes ] section
                lig_atomtypes_section = lig_atomtypes_section[2:]

                # Remove the [ atomtypes ] section from top_lines
                top_lines = [line for line in top_lines if line not in top_atomtypes_section]

            # NOTE: Check for repeated atoms in the [ atomtypes ] section
            # NOTE: raise error if there are conflicts - atoms named equally with different parameters
            # NOTE: raise error if there are different number of columns in the atomtypes sections

            top_lines.insert(ff_index + 1, "\n")

            # Merge both [ atomtypes ] sections
            atomtype_section = top_atomtypes_section + lig_atomtypes_section

            # Write the merged [ atomtypes ] section into the main topology after the forcefield include
            for atomtype_index in range(len(atomtype_section)):
                top_lines.insert(ff_index + atomtype_index + 2, atomtype_section[atomtype_index])

            # Update the index for the remaining directives
            at_index = ff_index + atomtype_index + 2
        else:
            at_index = ff_index

        top_lines.insert(at_index + 1, "\n")
        top_lines.insert(at_index + 2, "; Including ligand ITP\n")
        top_lines.insert(at_index + 3, '#include "' + itp_name + '"\n')
        top_lines.insert(at_index + 4, "\n")
        if self.io_dict["in"].get("input_posres_itp_path"):
            top_lines.insert(at_index + 5, "; Ligand position restraints" + "\n")
            top_lines.insert(at_index + 6, "#ifdef " + self.posres_name + "\n")
            top_lines.insert(
                at_index + 7,
                '#include "' + str(Path(self.io_dict["in"].get("input_posres_itp_path", "")).name) + '"\n'
            )
            top_lines.insert(at_index + 8, "#endif" + "\n")
            top_lines.insert(at_index + 9, "\n")

        inside_moleculetype_section = False
        with open(self.io_dict["in"].get("input_itp_path", "")) as itp_file:
            moleculetype_pattern = r"\[ moleculetype \]"
            for line in itp_file:
                if re.search(moleculetype_pattern, line):
                    inside_moleculetype_section = True
                    continue
                if inside_moleculetype_section and not line.startswith(";"):
                    moleculetype = line.strip().split()[0].strip()
                    break

        molecules_pattern = r"\[ molecules \]"
        inside_molecules_section = False
        index_molecule = None
        molecule_string = (
            str(moleculetype) + int(20 - len(moleculetype)) * " " + "1" + "\n"
        )
        for index, line in enumerate(top_lines):
            if re.search(molecules_pattern, line):
                inside_molecules_section = True
                continue
            if (
                inside_molecules_section and not line.startswith(";") and line.upper().startswith("PROTEIN")
            ):
                index_molecule = index

        if index_molecule:
            top_lines.insert(index_molecule + 1, molecule_string)
        else:
            top_lines.append(molecule_string)

        new_top = fu.create_name(
            path=top_dir, prefix=self.prefix, step=self.step, name="ligand.top"
        )

        with open(new_top, "w") as new_top_f:
            new_top_f.write("".join(top_lines))

        # Create a new itp ligand file without the [ atomtypes ] section
        new_ligand_tip_path = str(Path(top_dir) / itp_name)
        with open(new_ligand_tip_path, 'w') as new_itp_file:
            new_itp_file.write("".join(remaining_itp_contents))

        if self.io_dict["in"].get("input_posres_itp_path"):
            shutil.copy2(self.io_dict["in"].get("input_posres_itp_path", ""), top_dir)

        # zip topology
        fu.log(
            "Compressing topology to: %s"
            % self.io_dict["out"].get("output_top_zip_path"),
            self.out_log,
            self.global_log,
        )
        fu.zip_top(
            zip_file=self.io_dict["out"].get("output_top_zip_path", ""),
            top_file=new_top,
            out_log=self.out_log,
            remove_original_files=self.remove_tmp
        )

        # Remove temporal files
        self.tmp_files.append(top_dir)
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)
        return 0


def append_ligand(
    input_top_zip_path: str,
    input_itp_path: str,
    output_top_zip_path: str,
    input_posres_itp_path: Optional[str] = None,
    properties: Optional[dict] = None,
    **kwargs,
) -> int:
    """Create :class:`AppendLigand <gromacs_extra.append_ligand.AppendLigand>` class and
    execute the :meth:`launch() <gromacs_extra.append_ligand.AppendLigand.launch>` method."""
    return AppendLigand(
        input_top_zip_path=input_top_zip_path,
        input_itp_path=input_itp_path,
        output_top_zip_path=output_top_zip_path,
        input_posres_itp_path=input_posres_itp_path,
        properties=properties,
        **kwargs,
    ).launch()


append_ligand.__doc__ = AppendLigand.__doc__


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(
        description="Wrapper of the GROMACS editconf module.",
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
    required_args.add_argument("--input_top_zip_path", required=True)
    required_args.add_argument("--input_itp_path", required=True)
    required_args.add_argument("--output_top_zip_path", required=True)
    parser.add_argument("--input_posres_itp_path", required=False)

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    append_ligand(
        input_top_zip_path=args.input_top_zip_path,
        input_itp_path=args.input_itp_path,
        output_top_zip_path=args.output_top_zip_path,
        input_posres_itp_path=args.input_posres_itp_path,
        properties=properties,
    )


if __name__ == "__main__":
    main()
