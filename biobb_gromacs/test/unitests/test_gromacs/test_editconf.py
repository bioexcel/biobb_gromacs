# type: ignore
import os
import sys
from pathlib import Path

import pytest
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

    def test_editconf_gmx_lib(self):
        gmx_lib = Path(os.environ.get('CONDA_PREFIX', sys.prefix)) / 'share' / 'gromacs' / 'top'
        if not gmx_lib.is_dir():
            pytest.skip(f'GROMACS share/top directory not found: {gmx_lib}')
        properties = {**self.properties, 'gmx_lib': str(gmx_lib)}
        paths = {**self.paths, 'output_gro_path': 'output_gro_gmx_lib.gro'}
        editconf(properties=properties, **paths)
        assert fx.not_empty(paths['output_gro_path'])
        assert fx.equal(paths['output_gro_path'], paths['ref_output_gro_path'])
