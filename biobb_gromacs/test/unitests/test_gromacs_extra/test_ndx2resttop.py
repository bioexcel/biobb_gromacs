# type: ignore
from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs_extra.ndx2resttop import Ndx2resttop


class TestNdx2resttop():
    def setup_class(self):
        fx.test_setup(self, 'ndx2resttop')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_ndx2resttop(self):
        returncode = Ndx2resttop(properties=self.properties, **self.paths).launch()
        assert fx.not_empty(self.paths['output_top_zip_path'])
        # assert fx.equal(self.paths['output_top_zip_path'], self.paths['ref_output_top_zip_path'])
        assert fx.exe_success(returncode)
