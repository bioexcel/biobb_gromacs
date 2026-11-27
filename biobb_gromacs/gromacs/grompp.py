#!/usr/bin/env python3

"""Module containing the Grompp class and the command line interface."""
from typing import Optional
from pathlib import Path, PurePath
from biobb_common.generic.biobb_object import launcher
from biobb_common.tools import file_utils as fu
from biobb_gromacs.gromacs.common import GromacsBlock
from biobb_gromacs.gromacs.common import create_mdp
from biobb_gromacs.gromacs.common import mdp_preset


class Grompp(GromacsBlock):
    """
    | biobb_gromacs Grompp
    | Wrapper of the `GROMACS grompp <http://manual.gromacs.org/current/onlinehelp/gmx-grompp.html>`_ module.
    | The GROMACS preprocessor module needs to be fed with the input system and the dynamics parameters to create a portable binary run input file TPR. The simulation parameters can be specified by two methods:  1.The predefined mdp settings defined at simulation_type property or  2.A custom mdp file defined at the input_mdp_path argument.  These two methods are mutually exclusive. In both cases can be further modified by adding parameters to the mdp section in the yaml configuration file. The simulation parameter names and default values can be consulted in the `official MDP specification <http://manual.gromacs.org/current/user-guide/mdp-options.html>`_.

    Args:
        input_gro_path (str): Path to the input GROMACS structure GRO file. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/grompp.gro>`_. Accepted formats: gro (edam:format_2033).
        input_top_zip_path (str): Path to the input GROMACS topology TOP and ITP files in zip format. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/grompp.zip>`_. Accepted formats: zip (edam:format_3987).
        output_tpr_path (str): Path to the output portable binary run file TPR. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_grompp.tpr>`_. Accepted formats: tpr (edam:format_2333).
        input_cpt_path (str) (Optional): Path to the input GROMACS checkpoint file CPT. File type: input. Accepted formats: cpt (edam:format_2333).
        input_ndx_path (str) (Optional): Path to the input GROMACS index files NDX. File type: input. Accepted formats: ndx (edam:format_2033).
        input_mdp_path (str) (Optional): Path to the input GROMACS `MDP file <http://manual.gromacs.org/current/user-guide/mdp-options.html>`_. File type: input. Accepted formats: mdp (edam:format_2330).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **mdp** (*dict*) - ({}) MDP options specification.
            * **simulation_type** (*str*) - (None) Default options for the mdp file. Each one creates a different mdp file. Values: `minimization <https://biobb-gromacs.readthedocs.io/en/latest/_static/mdp/minimization.mdp>`_ (Energy minimization using steepest descent algorithm is used), `nvt <https://biobb-gromacs.readthedocs.io/en/latest/_static/mdp/nvt.mdp>`_ (substance N Volume V and Temperature T are conserved), `npt <https://biobb-gromacs.readthedocs.io/en/latest/_static/mdp/npt.mdp>`_ (substance N pressure P and Temperature T are conserved), `free <https://biobb-gromacs.readthedocs.io/en/latest/_static/mdp/free.mdp>`_ (No design constraints applied; Free MD), `ions <https://biobb-gromacs.readthedocs.io/en/latest/_static/mdp/minimization.mdp>`_ (Synonym of minimization), index (Creates an empty mdp file).
            * **maxwarn** (*int*) - (0) [0~1000|1] Maximum number of allowed warnings. The default is 10 when simulation_type is a preset (not index).
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

            from biobb_gromacs.gromacs.grompp import grompp

            prop = { 'simulation_type': 'minimization',
                     'mdp':
                        { 'emtol':'500',
                          'nsteps':'5000'}}
            grompp(input_gro_path='/path/to/myStructure.gro',
                   input_top_zip_path='/path/to/myTopology.zip',
                   output_tpr_path='/path/to/newCompiledBin.tpr',
                   properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS Grompp
            * version: 2025.2
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_gro_path: str, input_top_zip_path: str, output_tpr_path: str,
                 input_cpt_path: Optional[str] = None, input_ndx_path: Optional[str] = None, input_mdp_path: Optional[str] = None,
                 properties: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**locals())

        # Should not be copied inside container
        self.input_top_zip_path = self.io_dict["in"].pop("input_top_zip_path")

        # Properties specific for BB
        self.output_mdp_path = self.properties.get('output_mdp_path', 'grompp.mdp')
        self.output_top_path = self.properties.get('output_top_path', 'grompp.top')
        self.maxwarn = str(self.maxwarn)
        if self.simulation_type and self.simulation_type != 'index':
            self.maxwarn = str(self.properties.get('maxwarn', 10))
        self.mdp = {k: str(v) for k, v in self.mdp.items()}

    def run(self) -> None:
        """Execute the :class:`Grompp <gromacs.grompp.Grompp>` object."""

        # Unzip topology to topology_out
        top_file = fu.unzip_top(zip_file=self.input_top_zip_path, out_log=self.out_log, unique_dir=self.stage_io_dict.get("unique_dir", ""))

        # Create MDP file
        self.output_mdp_path = self._create_mdp(str(Path(self.stage_io_dict.get("unique_dir", "")).joinpath(self.output_mdp_path)))

        self.cmd = [self.binary_path, 'grompp',
                    '-f', self.staged_path(self.output_mdp_path),
                    '-c', self.stage_io_dict["in"]["input_gro_path"],
                    '-r', self.stage_io_dict["in"]["input_gro_path"],
                    '-p', self.staged_path(top_file),
                    '-o', self.stage_io_dict["out"]["output_tpr_path"],
                    '-po', self.staged_path(self.create_tmp_file('mdout.mdp')),
                    '-maxwarn', self.maxwarn]

        if self.stage_io_dict["in"].get("input_cpt_path"):
            self.cmd.append('-t')
            self.cmd.append(self.stage_io_dict["in"]["input_cpt_path"])
        if self.stage_io_dict["in"].get("input_ndx_path"):
            self.cmd.append('-n')
            self.cmd.append(self.stage_io_dict["in"]["input_ndx_path"])

        # Run Biobb block
        self.run_biobb()

    def write_parameter_files(self, directory: str) -> list[str]:
        """Write the MDP file to **directory** without executing grompp, used by the
        provenance of the executions skipped by the restart property."""
        return [self._create_mdp(str(Path(directory).joinpath(PurePath(self.output_mdp_path).name)))]

    def _create_mdp(self, output_mdp_path: str) -> str:
        """Create the MDP file from the simulation_type preset, the input_mdp_path file and the mdp property."""
        return create_mdp(output_mdp_path=output_mdp_path,
                          input_mdp_path=self.io_dict["in"]["input_mdp_path"],
                          preset_dict=mdp_preset(self.simulation_type),
                          mdp_properties_dict=self.mdp)


grompp = launcher(Grompp)


if __name__ == '__main__':
    Grompp.main()
