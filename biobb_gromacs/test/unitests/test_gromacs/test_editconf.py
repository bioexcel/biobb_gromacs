from biobb_common.tools import test_fixtures as fx
from biobb_gromacs.gromacs.editconf import editconf


class TestEditconf:
    def setup_class(self):
        fx.test_setup(self, 'editconf')

    def teardown_class(self):
        # pass
        fx.test_teardown(self)

    def test_editconf(self):
        editconf(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_gro_path'])
        assert fx.equal(self.paths['output_gro_path'], self.paths['ref_output_gro_path'])
