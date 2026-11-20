# type: ignore
from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.solvate import solvate


class TestSolvate():
    def setup_class(self):
        fx.test_setup(self, 'solvate')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_solvate(self):
        returncode = solvate(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_gro_path'])
        assert fx.equal(self.paths['output_gro_path'], self.paths['ref_output_gro_path'])
        assert fx.not_empty(self.paths['output_top_zip_path'])
        assert fx.equal(self.paths['output_top_zip_path'], self.paths['ref_output_top_zip_path'])
        assert fx.exe_success(returncode)


class TestSolvateTip4p():
    def setup_class(self):
        fx.test_setup(self, 'solvate_tip4p')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_solvate_tip4p(self):
        returncode = solvate(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_gro_path'])
        assert fx.not_empty(self.paths['output_top_zip_path'])
        assert fx.exe_success(returncode)
        # The tip4p.gro solvent box adds the virtual site (MW) of the 4-point water model
        with open(self.paths['output_gro_path']) as gro_file:
            assert any(line[10:15].strip() == 'MW' for line in gro_file)
