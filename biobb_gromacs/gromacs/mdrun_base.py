#!/usr/bin/env python3

"""Module containing the MdrunBase class shared by the GROMACS mdrun building blocks."""
import re
import shutil
import pathlib
from typing import ClassVar
from biobb_common.tools import file_utils as fu
from biobb_gromacs.gromacs.common import GromacsBlock


class MdrunBase(GromacsBlock):
    """Shared behaviour for the GROMACS ``mdrun`` building blocks
    (:class:`Mdrun <gromacs.mdrun.Mdrun>`,
    :class:`MdrunPlumed <gromacs.mdrun_plumed.MdrunPlumed>` and
    :class:`MdrunMultidir <gromacs.mdrun_multidir.MdrunMultidir>`).

    :meth:`run` executes mdrun with the flags of the staged files (:meth:`mdrun_arguments`),
    the CPU/GPU/thread flags and the MPI runner prefix. This base class also stages the outputs
    that a checkpoint restart appends to and follows the ``-noappend`` output renaming.
    """

    # mdrun flag of each file argument
    mdrun_flags: ClassVar[dict[str, str]] = {
        "input_tpr_path": "-s", "output_gro_path": "-c", "output_edr_path": "-e", "output_log_path": "-g",
        "output_trr_path": "-o", "input_cpt_path": "-cpi", "output_xtc_path": "-x", "output_cpt_path": "-cpo",
        "output_dhdl_path": "-dhdl"}

    def run(self) -> None:
        """Execute mdrun with the arguments of the block (:meth:`mdrun_arguments`), the
        CPU/GPU/thread flags and the MPI runner."""
        self.cmd = [self.binary_path, 'mdrun'] + self.mdrun_arguments()
        self._append_gmx_runtime_flags()
        self._prepend_mpi_runner()
        self.run_biobb()

    def mdrun_arguments(self) -> list[str]:
        """Go from the staged files to their mdrun flags (``mdrun_flags``), with ``-cpt`` for the output checkpoint."""
        arguments = []
        for file_ref, flag in self.mdrun_flags.items():
            file_path = self.stage_io_dict["in"].get(file_ref) or self.stage_io_dict["out"].get(file_ref)
            if file_path:
                arguments += [flag, str(file_path)]
        if self.stage_io_dict["out"].get("output_cpt_path") and self.checkpoint_time:
            arguments += ['-cpt', str(self.checkpoint_time)]
        return arguments

    def stage_files(self):
        """Stage the files in the sandbox, plus the outputs a checkpoint restart appends to."""
        super().stage_files()
        self._stage_outputs_to_append()

    def _stage_outputs_to_append(self) -> None:
        """Copy the existing output files of the previous simulation part into the sandbox.

        When continuing from a checkpoint (``input_cpt_path``) without ``-noappend``,
        GROMACS appends to the output files listed in the checkpoint and refuses to
        start if they are not present in the working directory. As every execution
        runs in a new sandbox, copy the output files that already exist on the host
        into it, so mdrun can append to them (GROMACS checks their checksums).
        """
        input_cpt_path = self.io_dict.get("in", {}).get("input_cpt_path")
        if self.noappend or self.disable_sandbox or not input_cpt_path or not pathlib.Path(input_cpt_path).is_file():
            return
        unique_dir = pathlib.Path(self.stage_io_dict["unique_dir"])
        for file_path in self.io_dict.get("out", {}).values():
            if not file_path or not pathlib.Path(file_path).is_file():
                continue
            sandbox_file_path = unique_dir / pathlib.Path(file_path).name
            # Do not overwrite the staged inputs, ie: input_cpt_path is also the output_cpt_path
            if sandbox_file_path.exists():
                continue
            fu.log(f"Copy to stage to append to it: {file_path} --> {unique_dir.name}", self.out_log)
            shutil.copy2(file_path, sandbox_file_path)

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
        """Append the shared CPU/GPU/thread flags to ``self.cmd`` and set OMP_NUM_THREADS."""
        # gromacs cpu mpi/openmp properties: 0 lets GROMACS guess
        if self.num_threads:
            fu.log(f'User added number of gmx threads: {self.num_threads}', self.out_log)
            self.cmd.append('-nt')
            self.cmd.append(str(self.num_threads))
        if self.num_threads_mpi:
            fu.log(f'User added number of gmx mpi threads: {self.num_threads_mpi}', self.out_log)
            self.cmd.append('-ntmpi')
            self.cmd.append(str(self.num_threads_mpi))
        if self.num_threads_omp:
            fu.log(f'User added number of gmx omp threads: {self.num_threads_omp}', self.out_log)
            self.cmd.append('-ntomp')
            self.cmd.append(str(self.num_threads_omp))
        if self.num_threads_omp_pme:
            fu.log(f'User added number of gmx omp_pme threads: {self.num_threads_omp_pme}', self.out_log)
            self.cmd.append('-ntomp_pme')
            self.cmd.append(str(self.num_threads_omp_pme))
        # GMX gpu properties
        if self.use_gpu:
            fu.log('Adding GPU specific settings adds: -nb gpu -pme gpu', self.out_log)
            self.cmd += ["-nb", "gpu", "-pme", "gpu"]
        # Device ids: 0 (ie: from YAML) is a valid one
        if self.gpu_id is not None and str(self.gpu_id):
            fu.log(f'list of unique GPU device IDs available to use: {self.gpu_id}', self.out_log)
            self.cmd.append('-gpu_id')
            self.cmd.append(str(self.gpu_id))
        if self.gpu_tasks is not None and str(self.gpu_tasks):
            fu.log(f'list of GPU device IDs, mapping each PP task on each node to a device: {self.gpu_tasks}', self.out_log)
            self.cmd.append('-gputasks')
            self.cmd.append(str(self.gpu_tasks))

        if self.noappend:
            self.cmd.append('-noappend')

        # GROMACS aborts when OMP_NUM_THREADS (inherited, e.g. from Slurm, or set
        # in env_vars_dict) differs from -ntomp, so pin it to num_threads_omp for
        # the mdrun process only (env_vars_dict is a copy, see GromacsBlock).
        num_threads_omp = str(self.num_threads_omp)
        if num_threads_omp.isdigit() and int(num_threads_omp) > 0:
            user_omp = self.env_vars_dict.get('OMP_NUM_THREADS')
            if user_omp is not None and str(user_omp) != num_threads_omp:
                fu.log(f'WARNING: OMP_NUM_THREADS={user_omp} in env_vars_dict is replaced by num_threads_omp={num_threads_omp}, GROMACS requires both to match', self.out_log, self.global_log)
            fu.log(f'Setting OMP_NUM_THREADS={num_threads_omp} for the mdrun process to match -ntomp', self.out_log)
            self.env_vars_dict['OMP_NUM_THREADS'] = num_threads_omp

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
