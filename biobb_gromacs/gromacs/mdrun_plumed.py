#!/usr/bin/env python3

"""Module containing the MDrun class and the command line interface."""
import os
import shutil
from pathlib import PurePath
from typing import Optional
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_gromacs.gromacs.mdrun_base import MdrunBase


class MdrunPlumed(MdrunBase):
    """
    | biobb_gromacs MdrunPlumed
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
        input_plumed_path (str) (Optional): Path to the main PLUMED input file. If provided, PLUMED will be used during the simulation. All files used by the main PLUMED input file must exist in the input_plumed_folder and be called with just their name. Make sure to provide a GROMACS version with the PLUMED patch. File type: input. Accepted formats: dat (edam:format_2330).
        input_plumed_folder (dir) (Optional): Path to the folder with all files needed by the main PLUMED input file, see input_plumed_path. File type: input. Accepted formats: directory (edam:format_1915)
        output_plumed_folder (dir) (Optional): Folder where PLUMED generated output files will be saved. File type: output. Accepted formats: directory (edam:format_1915)
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **mpi_bin** (*str*) - (None) Path to the MPI runner. Usually "mpirun" or "srun".
            * **mpi_np** (*int*) - (0) [0~1000|1] Number of MPI processes. Usually an integer bigger than 1.
            * **mpi_flags** (*str*) - (None) Path to the MPI hostlist file.
            * **checkpoint_time** (*int*) - (15) [0~1000|1] Checkpoint writing interval in minutes. Only enabled if an output_cpt_path is provided.
            * **noappend** (*bool*) - (False) Include the noappend flag to open new output files and add the simulation part number to all output file names
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

            from biobb_gromacs.gromacs.mdrun_plumed import mdrun_plumed
            prop = { 'num_threads': 0,
                     'binary_path': 'gmx' }
            mdrun_plumed(input_tpr_path='/path/to/myPortableBinaryRunInputFile.tpr',
                        output_trr_path='/path/to/newTrajectory.trr',
                        output_gro_path='/path/to/newStructure.gro',
                        output_edr_path='/path/to/newEnergy.edr',
                        output_log_path='/path/to/newSimulationLog.log',
                        properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS Mdrun with PLUMED
            * version: 2025.2
            * license: LGPL 2.1
            * multinode: mpi
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_tpr_path: str, output_gro_path: str, output_edr_path: str,
                 output_log_path: str, output_trr_path: Optional[str] = None, input_cpt_path: Optional[str] = None,
                 output_xtc_path: Optional[str] = None, output_cpt_path: Optional[str] = None,
                 output_dhdl_path: Optional[str] = None, input_plumed_path: Optional[str] = None,
                 input_plumed_folder: Optional[str] = None, output_plumed_folder: Optional[str] = None,
                 properties: Optional[dict] = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_tpr_path": input_tpr_path, "input_cpt_path": input_cpt_path,
                   "input_plumed_path": input_plumed_path, "input_plumed_folder": input_plumed_folder},
            "out": {"output_trr_path": output_trr_path, "output_gro_path": output_gro_path,
                    "output_edr_path": output_edr_path, "output_log_path": output_log_path,
                    "output_xtc_path": output_xtc_path, "output_cpt_path": output_cpt_path,
                    "output_dhdl_path": output_dhdl_path, "output_plumed_folder": output_plumed_folder}
        }

        # Properties specific for BB
        self._init_common_properties(properties)

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`MdrunPlumed <gromacs.mdrun_plumed.MdrunPlumed>` object."""

        # Setup Biobb
        if self.check_restart():
            return 0

        self.stage_files()

        working_dir = self._get_working_dir()

        self.cmd = [self.binary_path, 'mdrun',
                    '-s', PurePath(self.stage_io_dict["in"]["input_tpr_path"]).name,
                    '-c', PurePath(self.stage_io_dict["out"]["output_gro_path"]).name,
                    '-e', PurePath(self.stage_io_dict["out"]["output_edr_path"]).name,
                    '-g', PurePath(self.stage_io_dict["out"]["output_log_path"]).name]

        if self.stage_io_dict["out"].get("output_trr_path"):
            self.cmd.append('-o')
            self.cmd.append(PurePath(self.stage_io_dict["out"]["output_trr_path"]).name)

        if self.stage_io_dict["in"].get("input_plumed_path"):
            self.cmd.append('-plumed')
            self.cmd.append(PurePath(self.stage_io_dict["in"]["input_plumed_path"]).name)

        if self.stage_io_dict["in"].get("input_cpt_path"):
            self.cmd.append('-cpi')
            self.cmd.append(PurePath(self.stage_io_dict["in"]["input_cpt_path"]).name)
        if self.stage_io_dict["out"].get("output_xtc_path"):
            self.cmd.append('-x')
            self.cmd.append(PurePath(self.stage_io_dict["out"]["output_xtc_path"]).name)
        else:
            self.tmp_files.append('traj_comp.xtc')
        if self.stage_io_dict["out"].get("output_cpt_path"):
            self.cmd.append('-cpo')
            self.cmd.append(PurePath(self.stage_io_dict["out"]["output_cpt_path"]).name)
            if self.checkpoint_time:
                self.cmd.append('-cpt')
                self.cmd.append(str(self.checkpoint_time))
        if self.stage_io_dict["out"].get("output_dhdl_path"):
            self.cmd.append('-dhdl')
            self.cmd.append(PurePath(self.stage_io_dict["out"]["output_dhdl_path"]).name)

        # Shared mpi / working-directory / runtime flags
        self._prepend_mpi_runner()
        self.cmd = ["cd", working_dir, ";"] + self.cmd
        self._append_gmx_runtime_flags()

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Remove temporal files
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)
        return self.return_code

    def stage_files(self):
        """
        Stage the input/output files in a temporal unique directory aka sandbox.

        Overwrite the parent class method to handle PLUMED input files.
        """

        # If PLUMED is requested, change the working directory to the sandbox
        if self.io_dict["in"].get("input_plumed_path"):
            fu.log("PLUMED detected: Enabling chdir_sandbox to ensure relative paths work.", self.out_log)
            self.chdir_sandbox = True

        super().stage_files()

        # If plumed folder is provided, flatten its contents into the sandbox
        if self.stage_io_dict["in"].get("input_plumed_folder"):
            plumed_folder = self.stage_io_dict["in"]["input_plumed_folder"]
            for item in os.listdir(plumed_folder):
                s = os.path.join(plumed_folder, item)
                d = os.path.join(self.stage_io_dict["unique_dir"], item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

    def _extra_copy_to_host(self) -> None:
        """Copy PLUMED-generated output files from the sandbox to the host."""
        # Bulk Copy PLUMED outputs
        if self.io_dict["out"].get("output_plumed_folder"):
            dest_folder = self.io_dict["out"]["output_plumed_folder"]
            os.makedirs(dest_folder, exist_ok=True)

            unique_dir = self.stage_io_dict["unique_dir"]
            # We ignore files that were inputs
            input_filenames = [os.path.basename(f) for f in self.io_dict["in"].values() if f]
            # We ignore standard GMX outputs already copied
            gmx_output_filenames = [os.path.basename(f) for f in self.stage_io_dict["out"].values() if f and isinstance(f, str)]

            fu.log(f"Searching for PLUMED outputs in {unique_dir}...", self.out_log)
            for item in os.listdir(unique_dir):
                if item not in input_filenames and item not in gmx_output_filenames:
                    if os.path.isdir(os.path.join(unique_dir, item)):
                        # Skip directories
                        continue
                    # NOTE: Here we could list specific PLUMED output patterns or skip files contained in the input_plumed_folder
                    src = os.path.join(unique_dir, item)
                    dst = os.path.join(dest_folder, item)
                    fu.log(f"Copying PLUMED output: {item} --> {dest_folder}", self.out_log)
                    shutil.copy2(src, dst)


def mdrun_plumed(input_tpr_path: str, output_gro_path: str, output_edr_path: str,
                 output_log_path: str, output_trr_path: Optional[str] = None, input_cpt_path: Optional[str] = None,
                 output_xtc_path: Optional[str] = None, output_cpt_path: Optional[str] = None,
                 output_dhdl_path: Optional[str] = None, input_plumed_path: Optional[str] = None,
                 input_plumed_folder: Optional[str] = None, output_plumed_folder: Optional[str] = None,
                 properties: Optional[dict] = None, **kwargs) -> int:
    """Create :class:`MdrunPlumed <gromacs.mdrun_plumed.MdrunPlumed>` class and
    execute the :meth:`launch() <gromacs.mdrun_plumed.MdrunPlumed.launch>` method."""
    return MdrunPlumed(**dict(locals())).launch()


mdrun_plumed.__doc__ = MdrunPlumed.__doc__
main = MdrunPlumed.get_main(mdrun_plumed, "Wrapper for the GROMACS mdrun with PLUMED module.")


if __name__ == '__main__':
    main()
