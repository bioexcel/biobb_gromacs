# type: ignore
from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.grompp import grompp
from biobb_gromacs.gromacs.common import gmx_check
import pytest
import sys


class TestGromppDocker:
    def setup_class(self):
        fx.test_setup(self, 'grompp_docker')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_grompp_docker(self):
        returncode = grompp(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_tpr_path'])
        assert gmx_check(self.paths['output_tpr_path'], self.paths['ref_output_tpr_path'], gmx=self.properties.get('binary_path', 'gmx'))
        assert fx.exe_success(returncode)


@pytest.mark.skipif(sys.platform == 'darwin', reason="singularity not available on macOS")
class TestGromppSingularity:
    def setup_class(self):
        fx.test_setup(self, 'grompp_singularity')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_grompp_singularity(self):
        returncode = grompp(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_tpr_path'])
        assert gmx_check(self.paths['output_tpr_path'], self.paths['ref_output_tpr_path'], gmx=self.properties.get('binary_path', 'gmx'))
        assert fx.exe_success(returncode)
