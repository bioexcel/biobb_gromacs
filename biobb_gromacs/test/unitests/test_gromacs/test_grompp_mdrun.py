from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.grompp_mdrun import grompp_mdrun
from biobb_gromacs.gromacs.common import gmx_rms


class TestGromppMdrun:
    def setup_class(self):
        fx.test_setup(self, 'grompp_mdrun')

    def teardown_class(self):
        #pass
        fx.test_teardown(self)

    def test_grompp_mdrun(self):
        returncode = grompp_mdrun(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_trr_path'])
        assert gmx_rms(self.paths['output_trr_path'], self.paths['ref_output_trr_path'], self.paths['input_gro_path'], self.properties.get('binary_path','gmx'))
        assert fx.not_empty(self.paths['output_gro_path'])
        assert fx.not_empty(self.paths['output_edr_path'])
        assert fx.not_empty(self.paths['output_log_path'])
        assert fx.exe_success(returncode)
