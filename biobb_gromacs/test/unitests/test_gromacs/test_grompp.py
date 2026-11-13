# type: ignore
from pathlib import Path
from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.grompp import Grompp, grompp
from biobb_gromacs.gromacs.common import gmx_check, read_mdp


class TestGrompp():
    def setup_class(self):
        fx.test_setup(self, 'grompp')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_grompp(self):
        returncode = grompp(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_tpr_path'])
        assert gmx_check(self.paths['output_tpr_path'], self.paths['ref_output_tpr_path'], gmx=self.properties.get('binary_path', 'gmx'))
        assert fx.exe_success(returncode)

    def test_write_parameter_files(self, tmp_path):
        # The mdp is written without executing grompp (provenance of the executions skipped by restart)
        paths = {k: v for k, v in self.paths.items() if not k.startswith('ref_')}
        block = Grompp(properties={**self.properties, 'simulation_type': 'minimization'}, **paths)
        mdp_path, = block.write_parameter_files(str(tmp_path))
        assert Path(mdp_path) == tmp_path / 'grompp.mdp'
        mdp = read_mdp(mdp_path)
        assert mdp['integrator'] == 'steep' and mdp['ld-seed'] == '1'
