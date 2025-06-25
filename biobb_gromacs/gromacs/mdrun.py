#!/usr/bin/env python3

"""Module containing the MDrun class and the command line interface."""
import argparse
from typing import Optional
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_gromacs.gromacs.common import get_gromacs_version


class Mdrun(BiobbObject):
    """
    | biobb_gromacs Mdrun
    | Wrapper of the `GROMACS mdrun <http://manual.gromacs.org/current/onlinehelp/gmx-mdrun.html>`_ module.
    | MDRun is the main computational chemistry engine within GROMACS. It performs Molecular Dynamics simulations, but it can also perform Stochastic Dynamics, Energy Minimization, test particle insertion or (re)calculation of energies.

    Args:
        input_tpr_path (str): Path to the portable binary run input file TPR. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/mdrun.tpr>`_. Accepted formats: tpr (edam:format_2333).
        output_gro_path (str): Path to the output GROMACS structure GRO file. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_mdrun.gro>`_. Accepted formats: gro (edam:format_2033).
        output_edr_path (str): Path to the output GROMACS portable energy file EDR. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_mdrun.edr>`_. Accepted formats: edr (edam:format_2330).
        output_log_path (str): Path to the output GROMACS trajectory log file LOG. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_mdrun.log>`_. Accepted formats: log (edam:format_2330).
        output_trr_path (str) (Optional): Path to the GROMACS uncompressed raw trajectory file TRR. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_mdrun.trr>`_. Accepted formats: trr (edam:format_3910).
        input_cpt_path (str) (Optional): Path to the input GROMACS checkpoint file CPT. File type: input. Accepted formats: cpt (edam:format_2333).
        output_xtc_path (str) (Optional): Path to the GROMACS compressed trajectory file XTC. File type: output. Accepted formats: xtc (edam:format_3875).
        output_cpt_path (str) (Optional): Path to the output GROMACS checkpoint file CPT. File type: output. Accepted formats: cpt (edam:format_2333).
        output_dhdl_path (str) (Optional): Path to the output dhdl.xvg file only used when free energy calculation is turned on. File type: output. Accepted formats: xvg (edam:format_2033).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **mpi_bin** (*str*) - (None) Path to the MPI runner. Usually "mpirun" or "srun".
            * **mpi_np** (*int*) - (0) [0~1000|1] Number of MPI processes. Usually an integer bigger than 1.
            * **mpi_flags** (*str*) - (None) Path to the MPI hostlist file.
            * **checkpoint_time** (*int*) - (15) [0~1000|1] Checkpoint writing interval in minutes. Only enabled if an output_cpt_path is provided.
            * **num_threads** (*int*) - (0) [0~1000|1] Let GROMACS guess. The number of threads that are going to be used.
            * **num_threads_mpi** (*int*) - (0) [0~1000|1] Let GROMACS guess. The number of GROMACS MPI threads that are going to be used.
            * **num_threads_omp** (*int*) - (0) [0~1000|1] Let GROMACS guess. The number of GROMACS OPENMP threads that are going to be used.
            * **num_threads_omp_pme** (*int*) - (0) [0~1000|1] Let GROMACS guess. The number of GROMACS OPENMP_PME threads that are going to be used.
            * **use_gpu** (*bool*) - (False) Use settings appropriate for GPU. Adds: -nb gpu -pme gpu
            * **gpu_id** (*str*) - (None) list of unique GPU device IDs available to use.
            * **gpu_tasks** (*str*) - (None) list of GPU device IDs, mapping each PP task on each node to a device.
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

            from biobb_gromacs.gromacs.mdrun import mdrun
            prop = { 'num_threads': 0,
                     'binary_path': 'gmx' }
            mdrun(input_tpr_path='/path/to/myPortableBinaryRunInputFile.tpr',
                  output_trr_path='/path/to/newTrajectory.trr',
                  output_gro_path='/path/to/newStructure.gro',
                  output_edr_path='/path/to/newEnergy.edr',
                  output_log_path='/path/to/newSimulationLog.log',
                  properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS Mdrun
            * version: 2024.5
            * license: LGPL 2.1
            * multinode: mpi
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_tpr_path: str, output_gro_path: str, output_edr_path: str,
                 output_log_path: str, output_trr_path: Optional[str] = None, input_cpt_path: Optional[str] = None,
                 output_xtc_path: Optional[str] = None, output_cpt_path: Optional[str] = None,
                 output_dhdl_path: Optional[str] = None, properties: Optional[dict] = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_tpr_path": input_tpr_path, "input_cpt_path": input_cpt_path},
            "out": {"output_trr_path": output_trr_path, "output_gro_path": output_gro_path,
                    "output_edr_path": output_edr_path, "output_log_path": output_log_path,
                    "output_xtc_path": output_xtc_path, "output_cpt_path": output_cpt_path,
                    "output_dhdl_path": output_dhdl_path}
        }

        # Properties specific for BB
        # general mpi properties
        self.mpi_bin = properties.get('mpi_bin')
        self.mpi_np = properties.get('mpi_np')
        self.mpi_flags = properties.get('mpi_flags')
        # gromacs cpu mpi/openmp properties
        self.num_threads = str(properties.get('num_threads', ''))
        self.num_threads_mpi = str(properties.get('num_threads_mpi', ''))
        self.num_threads_omp = str(properties.get('num_threads_omp', ''))
        self.num_threads_omp_pme = str(properties.get('num_threads_omp_pme', ''))
        # gromacs gpus
        self.use_gpu = properties.get('use_gpu', False)  # Adds: -nb gpu -pme gpu
        self.gpu_id = str(properties.get('gpu_id', ''))
        self.gpu_tasks = str(properties.get('gpu_tasks', ''))
        # gromacs
        self.checkpoint_time = properties.get('checkpoint_time')

        # Properties common in all GROMACS BB
        self.gmx_lib = properties.get('gmx_lib', None)
        self.binary_path: str = properties.get('binary_path', 'gmx')
        self.gmx_nobackup = properties.get('gmx_nobackup', True)
        self.gmx_nocopyright = properties.get('gmx_nocopyright', True)
        if self.gmx_nobackup:
            self.binary_path += ' -nobackup'
        if self.gmx_nocopyright:
            self.binary_path += ' -nocopyright'
        if (not self.mpi_bin) and (not self.container_path):
            self.gmx_version = get_gromacs_version(self.binary_path)

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Mdrun <gromacs.mdrun.Mdrun>` object."""

        # Setup Biobb
        if self.check_restart():
            return 0

        # Optional output files (if not added mrun will create them using a generic name)
        if not self.stage_io_dict["out"].get("output_trr_path"):
            self.stage_io_dict["out"]["output_trr_path"] = fu.create_name(prefix=self.prefix, step=self.step, name='trajectory.trr')
            self.tmp_files.append(self.stage_io_dict["out"]["output_trr_path"])

        self.stage_files()

        self.cmd = [self.binary_path, 'mdrun',
                    '-o', self.stage_io_dict["out"]["output_trr_path"],
                    '-s', self.stage_io_dict["in"]["input_tpr_path"],
                    '-c', self.stage_io_dict["out"]["output_gro_path"],
                    '-e', self.stage_io_dict["out"]["output_edr_path"],
                    '-g', self.stage_io_dict["out"]["output_log_path"]]

        if self.stage_io_dict["in"].get("input_cpt_path"):
            self.cmd.append('-cpi')
            self.cmd.append(self.stage_io_dict["in"]["input_cpt_path"])
        if self.stage_io_dict["out"].get("output_xtc_path"):
            self.cmd.append('-x')
            self.cmd.append(self.stage_io_dict["out"]["output_xtc_path"])
        else:
            self.tmp_files.append('traj_comp.xtc')
        if self.stage_io_dict["out"].get("output_cpt_path"):
            self.cmd.append('-cpo')
            self.cmd.append(self.stage_io_dict["out"]["output_cpt_path"])
            if self.checkpoint_time:
                self.cmd.append('-cpt')
                self.cmd.append(str(self.checkpoint_time))
        if self.stage_io_dict["out"].get("output_dhdl_path"):
            self.cmd.append('-dhdl')
            self.cmd.append(self.stage_io_dict["out"]["output_dhdl_path"])

        # general mpi properties
        if self.mpi_bin:
            mpi_cmd = [self.mpi_bin]
            if self.mpi_np:
                mpi_cmd.append('-n')
                mpi_cmd.append(str(self.mpi_np))
            if self.mpi_flags:
                mpi_cmd.extend(self.mpi_flags)
            self.cmd = mpi_cmd + self.cmd

        # gromacs cpu mpi/openmp properties
        if self.num_threads:
            fu.log(f'User added number of gmx threads: {self.num_threads}', self.out_log)
            self.cmd.append('-nt')
            self.cmd.append(self.num_threads)
        if self.num_threads_mpi:
            fu.log(f'User added number of gmx mpi threads: {self.num_threads_mpi}', self.out_log)
            self.cmd.append('-ntmpi')
            self.cmd.append(self.num_threads_mpi)
        if self.num_threads_omp:
            fu.log(f'User added number of gmx omp threads: {self.num_threads_omp}', self.out_log)
            self.cmd.append('-ntomp')
            self.cmd.append(self.num_threads_omp)
        if self.num_threads_omp_pme:
            fu.log(f'User added number of gmx omp_pme threads: {self.num_threads_omp_pme}', self.out_log)
            self.cmd.append('-ntomp_pme')
            self.cmd.append(self.num_threads_omp_pme)
        # GMX gpu properties
        if self.use_gpu:
            fu.log('Adding GPU specific settings adds: -nb gpu -pme gpu', self.out_log)
            self.cmd += ["-nb", "gpu", "-pme", "gpu"]
        if self.gpu_id:
            fu.log(f'list of unique GPU device IDs available to use: {self.gpu_id}', self.out_log)
            self.cmd.append('-gpu_id')
            self.cmd.append(self.gpu_id)
        if self.gpu_tasks:
            fu.log(f'list of GPU device IDs, mapping each PP task on each node to a device: {self.gpu_tasks}', self.out_log)
            self.cmd.append('-gputasks')
            self.cmd.append(self.gpu_tasks)

        if self.gmx_lib:
            self.env_vars_dict['GMXLIB'] = self.gmx_lib

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Remove temporal files
        # self.tmp_files.append(self.stage_io_dict.get("unique_dir", ""))
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)
        return self.return_code


def mdrun(input_tpr_path: str, output_gro_path: str, output_edr_path: str,
          output_log_path: str, output_trr_path: Optional[str] = None, input_cpt_path: Optional[str] = None,
          output_xtc_path: Optional[str] = None, output_cpt_path: Optional[str] = None,
          output_dhdl_path: Optional[str] = None, properties: Optional[dict] = None, **kwargs) -> int:
    """Create :class:`Mdrun <gromacs.mdrun.Mdrun>` class and
    execute the :meth:`launch() <gromacs.mdrun.Mdrun.launch>` method."""

    return Mdrun(input_tpr_path=input_tpr_path, output_trr_path=output_trr_path,
                 output_gro_path=output_gro_path, output_edr_path=output_edr_path,
                 output_log_path=output_log_path, input_cpt_path=input_cpt_path,
                 output_xtc_path=output_xtc_path, output_cpt_path=output_cpt_path,
                 output_dhdl_path=output_dhdl_path, properties=properties,
                 **kwargs).launch()


mdrun.__doc__ = Mdrun.__doc__


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Wrapper for the GROMACS mdrun module.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('-c', '--config', required=False, help="This file can be a YAML file, JSON file or JSON string")

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_tpr_path', required=True)
    required_args.add_argument('--output_gro_path', required=True)
    required_args.add_argument('--output_edr_path', required=True)
    required_args.add_argument('--output_log_path', required=True)
    parser.add_argument('--output_trr_path', required=False)
    parser.add_argument('--input_cpt_path', required=False)
    parser.add_argument('--output_xtc_path', required=False)
    parser.add_argument('--output_cpt_path', required=False)
    parser.add_argument('--output_dhdl_path', required=False)

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    mdrun(input_tpr_path=args.input_tpr_path, output_trr_path=args.output_trr_path,
          output_gro_path=args.output_gro_path, output_edr_path=args.output_edr_path,
          output_log_path=args.output_log_path, input_cpt_path=args.input_cpt_path,
          output_xtc_path=args.output_xtc_path, output_cpt_path=args.output_cpt_path,
          output_dhdl_path=args.output_dhdl_path, properties=properties)


if __name__ == '__main__':
    main()
