#!/usr/bin/env python3

"""Module containing the Ndx2resttop class and the command line interface."""
import fnmatch
import argparse
from typing import Optional
from typing import Any
from pathlib import Path
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger


class Ndx2resttop(BiobbObject):
    """
    | biobb_gromacs Ndx2resttop
    | Generate a restrained topology from an index NDX file.
    | This module automatizes the process of restrained topology generation starting from an index NDX file.

    Args:
        input_ndx_path (str): Path to the input NDX index file. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs_extra/ndx2resttop.ndx>`_. Accepted formats: ndx (edam:format_2033).
        input_top_zip_path (str): Path the input TOP topology in zip format. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs_extra/ndx2resttop.zip>`_. Accepted formats: zip (edam:format_3987).
        output_top_zip_path (str): Path the output TOP topology in zip format. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs_extra/ref_ndx2resttop.zip>`_. Accepted formats: zip (edam:format_3987).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **posres_names** (*list*) - ("CUSTOM_POSRES") String with names of the position restraints to be included in the topology file separated by spaces. If provided it should match the length of the ref_rest_chain_triplet_list.
            * **force_constants** (*str*) - ("500 500 500") Array of three floats defining the force constants.
            * **ref_rest_chain_triplet_list** (*str*) - (None) Triplet list composed by (reference group, restrain group, chain) list.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_gromacs.gromacs_extra.ndx2resttop import ndx2resttop
            prop = { 'ref_rest_chain_triplet_list': '( Chain_A, Chain_A_noMut, A ), ( Chain_B, Chain_B_noMut, B ), ( Chain_C, Chain_C_noMut, C ), ( Chain_D, Chain_D_noMut, D )' }
            ndx2resttop(input_ndx_path='/path/to/myIndex.ndx',
                        input_top_zip_path='/path/to/myTopology.zip',
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

    def __init__(self, input_ndx_path: str, input_top_zip_path: str, output_top_zip_path: str,
                 properties: Optional[dict] = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_ndx_path": input_ndx_path, "input_top_zip_path": input_top_zip_path},
            "out": {"output_top_zip_path": output_top_zip_path}
        }

        # Properties specific for BB
        self.posres_names = properties.get('posres_names')
        self.force_constants = properties.get('force_constants', '500 500 500')
        self.ref_rest_chain_triplet_list = properties.get('ref_rest_chain_triplet_list')

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Ndx2resttop <gromacs_extra.ndx2resttop.Ndx2resttop>` object."""
        # Setup Biobb
        if self.check_restart():
            return 0

        top_file = fu.unzip_top(zip_file=self.io_dict['in'].get("input_top_zip_path", ""), out_log=self.out_log)

        # Create index list of index file (dictionary with the index of the start and stop lines of each group) :)
        index_dic: dict[str, Any] = {}
        lines = open(self.io_dict['in'].get("input_ndx_path", "")).read().splitlines()
        for index, line in enumerate(lines):

            # New group
            if line.startswith('['):
                index_dic[line] = [index, 0]

                # Update current group
                label = line

                # Close previous group
                if index > 0:
                    index_dic[label] = [index_dic[label][0], index]

            # Last group of the file
            if index == len(lines)-1:
                index_dic[label] = [index_dic[label][0], index]

        # Catch groups with just one line
        for label in index_dic.keys():
            if (index_dic[label][0]+1) == index_dic[label][1]:
                index_dic[label][1] += 1

        fu.log('Index_dic: '+str(index_dic), self.out_log, self.global_log)

        self.ref_rest_chain_triplet_list = [tuple(elem.strip(' ()').replace(' ', '').split(',')) for elem in str(self.ref_rest_chain_triplet_list).split('),')]
        fu.log('ref_rest_chain_triplet_list: ' + str(self.ref_rest_chain_triplet_list), self.out_log, self.global_log)

        if self.posres_names:
            self.posres_names = [elem.strip() for elem in self.posres_names.split()]
            fu.log('posres_names: ' + str(self.posres_names), self.out_log, self.global_log)
        else:
            self.posres_names = ['CUSTOM_POSRES']*len(self.ref_rest_chain_triplet_list)
            fu.log('posres_names: ' + str(self.posres_names), self.out_log, self.global_log)

        # Check if the number of posres_names matches the number of ref_rest_chain_triplet_list
        if len(self.posres_names) != len(self.ref_rest_chain_triplet_list):
            raise ValueError("If posres_names is provided, it should match the number of ref_rest_chain_triplet_list")

        for triplet, posre_name in zip(self.ref_rest_chain_triplet_list, self.posres_names):

            reference_group, restrain_group, chain = triplet

            fu.log('Reference group: '+reference_group, self.out_log, self.global_log)
            fu.log('Restrain group: '+restrain_group, self.out_log, self.global_log)
            fu.log('Chain: '+chain, self.out_log, self.global_log)
            self.io_dict['out']["output_itp_path"] = fu.create_name(path=str(Path(top_file).parent), prefix=self.prefix, step=self.step, name=restrain_group+'_posre.itp')

            # Mapping atoms from absolute enumeration to Chain relative enumeration
            fu.log('reference_group_index: start_closed:'+str(index_dic['[ '+reference_group+' ]'][0]+1)+' stop_open: '+str(index_dic['[ '+reference_group+' ]'][1]), self.out_log, self.global_log)
            reference_group_list = [int(elem) for line in lines[index_dic['[ '+reference_group+' ]'][0]+1: index_dic['[ '+reference_group+' ]'][1]] for elem in line.split()]
            fu.log('restrain_group_index: start_closed:'+str(index_dic['[ '+restrain_group+' ]'][0]+1)+' stop_open: '+str(index_dic['[ '+restrain_group+' ]'][1]), self.out_log, self.global_log)
            restrain_group_list = [int(elem) for line in lines[index_dic['[ '+restrain_group+' ]'][0]+1: index_dic['[ '+restrain_group+' ]'][1]] for elem in line.split()]
            selected_list = [reference_group_list.index(atom)+1 for atom in restrain_group_list]
            # Creating new ITP with restrains
            with open(self.io_dict['out'].get("output_itp_path", ''), 'w') as f:
                fu.log('Creating: '+str(f)+' and adding the selected atoms force constants', self.out_log, self.global_log)
                f.write('[ position_restraints ]\n')
                f.write('; atom  type      fx      fy      fz\n')
                for atom in selected_list:
                    f.write(str(atom)+'     1  '+self.force_constants+'\n')

            multi_chain = False
            # For multi-chain topologies
            # Including new ITP in the corresponding ITP-chain file
            for file_dir in Path(top_file).parent.iterdir():
                if "posre" not in file_dir.name and not file_dir.name.endswith("_pr.itp"):
                    if fnmatch.fnmatch(str(file_dir), "*_chain_"+chain+".itp"):
                        multi_chain = True
                        with open(str(file_dir), 'a') as f:
                            fu.log('Opening: '+str(f)+' and adding the ifdef include statement', self.out_log, self.global_log)
                            f.write('\n')
                            f.write('; Include Position restraint file\n')
                            f.write('#ifdef '+str(posre_name)+'\n')
                            f.write('#include "'+str(Path(self.io_dict['out'].get("output_itp_path", "")).name)+'"\n')
                            f.write('#endif\n')
                            f.write('\n')

            # For single-chain topologies
            # Including new ITP in the TOP file
            if not multi_chain:

                # Read all lines of the top file
                with open(top_file, 'r') as f:
                    lines = f.readlines()

                main_chain = False
                index = 0

                # Find the index of the line where the custom position restraints are going to be included
                for line in lines:

                    # Find the moleculetype directive of the main chain
                    if line.startswith('Protein_chain_'+chain):
                        main_chain = True
                        index = lines.index(line) + 3

                    # Find the end of the moleculetype directive of the main chain
                    if main_chain:
                        if line.startswith('[system]') or line.startswith('[molecules]') or line.startswith('#include ') or line.startswith('#ifdef POSRES'):
                            index = lines.index(line) - 1
                            break

                if index == 0:
                    raise ValueError(f"Protein_chain_{chain} not found in the topology file")

                # Include the custom position restraints in the top file
                lines.insert(index, '\n')
                lines.insert(index + 1, '; Include Position restraint file\n')
                lines.insert(index + 2, '#ifdef '+str(posre_name)+'\n')
                lines.insert(index + 3, '#include "'+str(Path(self.io_dict['out'].get("output_itp_path", "")).name)+'"\n')
                lines.insert(index + 4, '#endif\n')

                # Write the new top file
                with open(top_file, 'w') as f:
                    f.writelines(lines)

        # zip topology
        fu.zip_top(zip_file=self.io_dict['out'].get("output_top_zip_path", ""), top_file=top_file, out_log=self.out_log, remove_original_files=self.remove_tmp)

        # Remove temporal files
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)
        return 0


def ndx2resttop(input_ndx_path: str, input_top_zip_path: str, output_top_zip_path: str,
                properties: Optional[dict] = None, **kwargs) -> int:
    """Create :class:`Ndx2resttop <gromacs_extra.ndx2resttop.Ndx2resttop>` class and
    execute the :meth:`launch() <gromacs_extra.ndx2resttop.Ndx2resttop.launch>` method."""
    return Ndx2resttop(input_ndx_path=input_ndx_path,
                       input_top_zip_path=input_top_zip_path,
                       output_top_zip_path=output_top_zip_path,
                       properties=properties, **kwargs).launch()


ndx2resttop.__doc__ = Ndx2resttop.__doc__


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Wrapper for the GROMACS extra ndx2resttop module.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('-c', '--config', required=False, help="This file can be a YAML file, JSON file or JSON string")

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_ndx_path', required=True)
    required_args.add_argument('--input_top_zip_path', required=True)
    required_args.add_argument('--output_top_zip_path', required=True)

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    ndx2resttop(input_ndx_path=args.input_ndx_path, input_top_zip_path=args.input_top_zip_path,
                output_top_zip_path=args.output_top_zip_path, properties=properties)


if __name__ == '__main__':
    main()
