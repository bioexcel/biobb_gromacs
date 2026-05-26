# type: ignore
from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.convert_tpr import convert_tpr


class TestConvertTpr:
    def setup_class(self):
        fx.test_setup(self, 'convert_tpr')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_convert_tpr(self):
        convert_tpr(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_tpr_path'])
