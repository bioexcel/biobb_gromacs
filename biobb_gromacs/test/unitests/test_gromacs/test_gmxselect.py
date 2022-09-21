from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.gmxselect import gmxselect


class TestGmxselect:
    def setup_class(self):
        fx.test_setup(self, 'gmxselect')

    def teardown_class(self):
        #pass
        fx.test_teardown(self)

    def test_select(self):
        returncode = gmxselect(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_ndx_path'])
        assert fx.equal(self.paths['output_ndx_path'], self.paths['ref_output_ndx_path'])
        assert fx.exe_success(returncode)
