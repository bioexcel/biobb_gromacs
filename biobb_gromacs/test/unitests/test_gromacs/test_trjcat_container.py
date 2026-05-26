# type: ignore
from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.trjcat import trjcat
import pytest
import sys


class TestTrjcatDocker:
    def setup_class(self):
        fx.test_setup(self, 'trjcat_docker')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_trjcat_docker(self):
        returncode = trjcat(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_trj_path'])
        assert fx.equal(self.paths['output_trj_path'], self.paths['ref_output_trj_path'])
        assert fx.exe_success(returncode)


@pytest.mark.skipif(sys.platform == 'darwin', reason="singularity not available on macOS")
class TestTrjcatSingularity:
    def setup_class(self):
        fx.test_setup(self, 'trjcat_singularity')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_trjcat_singularity(self):
        returncode = trjcat(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_trj_path'])
        assert fx.equal(self.paths['output_trj_path'], self.paths['ref_output_trj_path'])
        assert fx.exe_success(returncode)
