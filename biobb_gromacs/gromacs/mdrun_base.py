#!/usr/bin/env python3

"""Module containing the MdrunBase class shared by the GROMACS mdrun building blocks."""
import re
import pathlib
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_gromacs.gromacs.common import get_gromacs_version


class MdrunBase(BiobbObject):
    """Shared behaviour for the GROMACS ``mdrun`` building blocks
    (:class:`Mdrun <gromacs.mdrun.Mdrun>`,
    :class:`MdrunPlumed <gromacs.mdrun_plumed.MdrunPlumed>` and
    :class:`MdrunMultidir <gromacs.mdrun_multidir.MdrunMultidir>`).

    Concrete subclasses declare their own ``self.io_dict`` and assemble the
    building-block-specific part of ``self.cmd`` in ``launch()``. This base
    class centralises the common GROMACS runtime properties, the MPI runner
    prefix, the CPU/GPU/thread command-line flags and the ``-noappend`` output
    renaming logic.
    """

    def _init_common_properties(self, properties: dict) -> None:
        """Parse the GROMACS runtime properties shared by all mdrun wrappers.

        Must be called from the subclass ``__init__`` after
        ``super().__init__(properties)`` (it relies on ``self.container_path``).
        """
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
        self.noappend = properties.get('noappend', False)

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

    def _get_working_dir(self) -> str:
        """Return the working directory for the command (container or sandbox)."""
        if self.container_path:
            return self.container_volume_path if self.container_volume_path else "/data"
        return self.stage_io_dict.get('unique_dir', '')

    def _prepend_mpi_runner(self) -> None:
        """Prepend the MPI runner (e.g. mpirun/srun) to ``self.cmd`` if configured."""
        if self.mpi_bin:
            mpi_cmd = [self.mpi_bin]
            if self.mpi_np:
                mpi_cmd.append('-n')
                mpi_cmd.append(str(self.mpi_np))
            if self.mpi_flags:
                mpi_cmd.append(self.mpi_flags)
            self.cmd = mpi_cmd + self.cmd

    def _append_gmx_runtime_flags(self) -> None:
        """Append the shared CPU/GPU/thread flags to ``self.cmd`` and set GMXLIB."""
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

        if self.noappend:
            self.cmd.append('-noappend')

        if self.gmx_lib:
            self.env_vars_dict['GMXLIB'] = self.gmx_lib

    def _apply_noappend_renaming(self) -> None:
        """Update expected output paths in the sandbox to catch -noappend renames.

        GROMACS mdrun changes output file names from md.gro to md.part0001.gro
        when the ``-noappend`` flag is used.
        """
        if not self.noappend:
            return

        def capture_part_pattern(filename):
            """Capture the 'part' pattern followed by digits from a string."""
            match = re.search(r'part\d+', filename)
            return match.group(0) if match else None

        # List files in the staging directory and find the part000x pattern
        staging_path = self.stage_io_dict["unique_dir"]
        files_in_staging = list(pathlib.Path(staging_path).glob('*'))
        part_pattern = None
        for file in files_in_staging:
            part_pattern = capture_part_pattern(file.name)
            if part_pattern:
                break

        # Update expected output files
        for file_ref, stage_file_path in self.stage_io_dict["out"].items():
            if stage_file_path:
                parent_path = pathlib.Path(stage_file_path).parent
                file_stem = pathlib.Path(stage_file_path).stem
                file_suffix = pathlib.Path(stage_file_path).suffix
                # Rename all output files except checkpoint files
                if file_suffix != '.cpt' and part_pattern:
                    new_file_name = f"{file_stem}.{part_pattern}{file_suffix}"
                    self.stage_io_dict["out"][file_ref] = str(parent_path / new_file_name)

    def _extra_copy_to_host(self) -> None:
        """Hook for subclasses to copy building-block-specific outputs. No-op by default."""

    def copy_to_host(self):
        """Copy output files back to the host, accounting for -noappend renames."""
        self._apply_noappend_renaming()
        super().copy_to_host()
        self._extra_copy_to_host()
