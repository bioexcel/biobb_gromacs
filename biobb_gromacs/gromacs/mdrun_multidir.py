#!/usr/bin/env python3

"""Module containing the MdrunMultidir class and the command line interface."""
import os
import shutil
from typing import Optional
from pathlib import PurePath
from biobb_common.tools.file_utils import launchlogger
from biobb_gromacs.gromacs.mdrun_base import MdrunBase


class MdrunMultidir(MdrunBase):
    """
    | biobb_gromacs MdrunMultidir
    | Wrapper of the `GROMACS mdrun <http://manual.gromacs.org/current/onlinehelp/gmx-mdrun.html>`_ module for `multidir setups <https://manual.gromacs.org/current/user-guide/mdrun-features.html#running-multi-simulations>`_.
    | MDRun is the main computational chemistry engine within GROMACS. It performs Molecular Dynamics simulations, but it can also perform Stochastic Dynamics, Energy Minimization, test particle insertion or (re)calculation of energies.

    Args:
        input_tpr_path (str): Path to the portable binary run input file TPR in each of the subdirectories. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs/mdrun.tpr>`_. Accepted formats: tpr (edam:format_2333).
        input_multifolder (dir): Path to the folder with all subdirectories for the multidir setup. File type: input. Accepted formats: directory (edam:format_1915)
        output_multifolder (dir): Folder where the generated output files will be saved. File type: output. Accepted formats: directory (edam:format_1915)
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **mpi_bin** (*str*) - (None) Path to the MPI runner. Usually "mpirun" or "srun".
            * **mpi_np** (*int*) - (0) [0~1000|1] Number of MPI processes. Usually an integer bigger than 1.
            * **mpi_flags** (*str*) - (None) Path to the MPI hostlist file.
            * **noappend** (*bool*) - (False) Include the noappend flag to open new output files and add the simulation part number to all output file names
            * **num_threads** (*int*) - (0) [0~1000|1] Let GROMACS guess. The number of threads that are going to be used.
            * **num_threads_mpi** (*int*) - (0) [0~1000|1] Let GROMACS guess. The number of GROMACS MPI threads that are going to be used.
            * **num_threads_omp** (*int*) - (0) [0~1000|1] Let GROMACS guess. The number of GROMACS OPENMP threads that are going to be used.
            * **num_threads_omp_pme** (*int*) - (0) [0~1000|1] Let GROMACS guess. The number of GROMACS OPENMP_PME threads that are going to be used.
            * **use_gpu** (*bool*) - (False) Use settings appropriate for GPU. Adds: -nb gpu -pme gpu
            * **gpu_id** (*str*) - (None) list of unique GPU device IDs available to use.
            * **gpu_tasks** (*str*) - (None) list of GPU device IDs, mapping each PP task on each node to a device.
            * **gmx_lib** (*str*) - (None) Path set GROMACS GMXLIB environment variable.
            * **binary_path** (*str*) - ("gmx_mpi") Path to the GROMACS executable binary.
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

            from biobb_gromacs.gromacs.mdrun_multidir import mdrun_multidir
            prop = { 'num_threads': 0,
                     'binary_path': 'gmx_bin' }
            mdrun_multidir(input_tpr_path='/path/to/myPortableBinaryRunInputFile.tpr',
                  input_multifolder='/path/to/inputMultidirFolder',
                  output_multifolder='/path/to/outputMultidirFolder',
                  properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS MdrunMultidir
            * version: 2025.2
            * license: LGPL 2.1
            * multinode: mpi
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self,
                 input_tpr_path: str,
                 input_multifolder: str,
                 output_multifolder: str,
                 properties: Optional[dict] = None,
                 **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {
                "input_tpr_path": input_tpr_path,
                "input_multifolder": input_multifolder
            },
            "out": {
                "output_multifolder": output_multifolder,
            }
        }

        # Properties specific for BB
        self._init_common_properties(properties)
        self.binary_path: str = properties.get('binary_path', 'gmx_bin')

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`MdrunMultidir <gromacs.mdrun_multidir.MdrunMultidir>` object."""

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        working_dir = self._get_working_dir()

        multifolder_path = self.stage_io_dict["in"]["input_multifolder"]
        subdirs = sorted(
            entry for entry in os.listdir(multifolder_path)
            if os.path.isdir(os.path.join(multifolder_path, entry))
        )
        self.cmd = [
            self.binary_path, 'mdrun',
            '-s', PurePath(self.stage_io_dict["in"]["input_tpr_path"]).name,
            '-multidir', ' '.join(subdirs),
        ]

        # Shared mpi / working-directory / runtime flags. multidir also needs to
        # cd into the multifolder so the -multidir subdir names resolve.
        self._prepend_mpi_runner()
        self.cmd = ["cd", working_dir, ";", 'cd',
                    PurePath(self.stage_io_dict["in"]["input_multifolder"]).name, ";"] + self.cmd
        self._append_gmx_runtime_flags()

        # Run Biobb block
        self.run_biobb()

        # Move files to output folder. When the input and output multifolders
        # share a basename they stage to the same sandbox path, so the move is
        # a no-op and must be skipped to avoid "move into itself" errors.
        input_multifolder = self.stage_io_dict["in"]["input_multifolder"]
        output_multifolder = self.stage_io_dict["out"]["output_multifolder"]
        if os.path.abspath(input_multifolder) != os.path.abspath(output_multifolder):
            shutil.copytree(input_multifolder, output_multifolder)
        # Copy files to host
        self.copy_to_host()

        # Remove temporal files
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)
        return self.return_code


def mdrun_multidir(input_tpr_path: str, input_multifolder: str, output_multifolder: str,
                   properties: Optional[dict] = None, **kwargs) -> int:
    """Create :class:`MdrunMultidir <gromacs.mdrun_multidir.MdrunMultidir>` class and
    execute the :meth:`launch() <gromacs.mdrun_multidir.MdrunMultidir.launch>` method."""
    return MdrunMultidir(**dict(locals())).launch()


mdrun_multidir.__doc__ = MdrunMultidir.__doc__
main = MdrunMultidir.get_main(mdrun_multidir, "Wrapper for the GROMACS mdrun module with multidir support.")


if __name__ == '__main__':
    main()
