# type: ignore
from pathlib import Path
from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.mdrun import mdrun, Mdrun
from biobb_gromacs.gromacs.convert_tpr import convert_tpr
from biobb_gromacs.gromacs.common import gmx_rms


class TestMdrun():
    def setup_class(self):
        fx.test_setup(self, 'mdrun')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_mdrun(self):
        returncode = mdrun(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_trr_path'])
        assert gmx_rms(self.paths['output_trr_path'], self.paths['ref_output_trr_path'], self.paths['input_tpr_path'], self.properties.get('binary_path', 'gmx'))
        assert fx.not_empty(self.paths['output_gro_path'])
        assert fx.not_empty(self.paths['output_edr_path'])
        assert fx.not_empty(self.paths['output_log_path'])
        assert fx.exe_success(returncode)

    def test_mdrun_restart_append(self):
        # Continue from a checkpoint appending to the output files of the previous part (issue #3)
        outputs = {'output_gro_path': 'restart.gro', 'output_edr_path': 'restart.edr',
                   'output_log_path': 'restart.log', 'output_trr_path': 'restart.trr',
                   'output_xtc_path': 'restart.xtc', 'output_cpt_path': 'restart.cpt'}
        for nsteps in (20, 40):
            convert_tpr(input_tpr_path=self.paths['input_tpr_path'], output_tpr_path=f'restart_{nsteps}.tpr',
                        properties={'nsteps': nsteps, 'binary_path': self.properties.get('binary_path', 'gmx')})
        assert fx.exe_success(mdrun(input_tpr_path='restart_20.tpr', properties=self.properties, **outputs))
        returncode = mdrun(input_tpr_path='restart_40.tpr', input_cpt_path='restart.cpt',
                           properties=self.properties, **outputs)
        assert fx.exe_success(returncode)
        assert 'appending to previous log file' in Path('restart.log').read_text()

    def test_mdrun_omp_num_threads_env(self):
        # num_threads_omp pins OMP_NUM_THREADS for the mdrun process only (issue #30)
        paths = {k: v for k, v in self.paths.items() if not k.startswith('ref_')}
        user_env = {'GMX_MAXBACKUP': '-1'}
        md = Mdrun(properties={**self.properties, 'num_threads_omp': 2, 'env_vars_dict': user_env}, **paths)
        md._append_gmx_runtime_flags()
        assert md.cmd[md.cmd.index('-ntomp') + 1] == '2'
        assert md.env_vars_dict == {'GMX_MAXBACKUP': '-1', 'OMP_NUM_THREADS': '2'}
        assert user_env == {'GMX_MAXBACKUP': '-1'}
        # A different OMP_NUM_THREADS in env_vars_dict is replaced, as GROMACS requires both to match
        user_env = {'OMP_NUM_THREADS': '3'}
        md = Mdrun(properties={**self.properties, 'num_threads_omp': 2, 'env_vars_dict': user_env}, **paths)
        md._append_gmx_runtime_flags()
        assert md.env_vars_dict['OMP_NUM_THREADS'] == '2'
        assert user_env == {'OMP_NUM_THREADS': '3'}
        # Unset or 0 (let GROMACS guess) does not touch the environment
        for props in (dict(self.properties), {**self.properties, 'num_threads_omp': 0}):
            md = Mdrun(properties=props, **paths)
            md._append_gmx_runtime_flags()
            assert 'OMP_NUM_THREADS' not in md.env_vars_dict
        # Without num_threads_omp, an OMP_NUM_THREADS in env_vars_dict is passed as is
        md = Mdrun(properties={**self.properties, 'env_vars_dict': {'OMP_NUM_THREADS': '3'}}, **paths)
        md._append_gmx_runtime_flags()
        assert md.env_vars_dict['OMP_NUM_THREADS'] == '3'
