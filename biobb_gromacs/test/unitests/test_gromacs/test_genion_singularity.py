from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.genion import genion
import pytest


class TestGenionSingularity:
    def setup_class(self):
        fx.test_setup(self, 'genion_singularity')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    @pytest.mark.skip(reason="singularity currently not available")
    def test_genion_singularity(self):
        returncode = genion(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_itp_path'])
        assert fx.equal(self.paths['output_itp_path'], self.paths['ref_output_itp_path'])
        assert fx.exe_success(returncode)
