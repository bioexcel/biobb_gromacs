# type: ignore
from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.trjcat import trjcat
import pytest


class TestSolvate():
    def setup_class(self):
        fx.test_setup(self, 'trjcat_singularity')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    @pytest.mark.skip(reason="singularity currently not available")
    def test_solvate(self):
        returncode = trjcat(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_trj_path'])
        assert fx.equal(self.paths['output_trj_path'], self.paths['ref_output_trj_path'])
        assert fx.exe_success(returncode)
