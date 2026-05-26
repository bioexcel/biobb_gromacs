# type: ignore
from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.gmxselect import gmxselect
import pytest
import sys


class TestGmxselectDocker:
    def setup_class(self):
        fx.test_setup(self, 'gmxselect_docker')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_gmxselect_docker(self):
        returncode = gmxselect(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_ndx_path'])
        assert fx.equal(self.paths['output_ndx_path'], self.paths['ref_output_ndx_path'])
        assert fx.exe_success(returncode)


@pytest.mark.skipif(sys.platform == 'darwin', reason="singularity not available on macOS")
class TestGmxselectSingularity:
    def setup_class(self):
        fx.test_setup(self, 'gmxselect_singularity')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_gmxselect_singularity(self):
        returncode = gmxselect(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_ndx_path'])
        assert fx.equal(self.paths['output_ndx_path'], self.paths['ref_output_ndx_path'])
        assert fx.exe_success(returncode)
