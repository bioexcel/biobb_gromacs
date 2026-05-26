# type: ignore
from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.convert_tpr import convert_tpr
import pytest
import sys


class TestConvertTprDocker:
    def setup_class(self):
        fx.test_setup(self, 'convert_tpr_docker')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_convert_tpr_docker(self):
        convert_tpr(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_tpr_path'])


@pytest.mark.skipif(sys.platform == 'darwin', reason="singularity not available on macOS")
class TestConvertTprSingularity:
    def setup_class(self):
        fx.test_setup(self, 'convert_tpr_singularity')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_convert_tpr_singularity(self):
        convert_tpr(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_tpr_path'])