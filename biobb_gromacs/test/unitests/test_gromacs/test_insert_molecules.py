# type: ignore
from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.insert_molecules import insert_molecules


class TestInsertMolecules():
    def setup_class(self):
        fx.test_setup(self, 'insert_molecules')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_insert_molecules(self):
        returncode = insert_molecules(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_gro_path'])
        assert fx.equal(self.paths['output_gro_path'], self.paths['ref_output_gro_path'])
        assert fx.exe_success(returncode)
