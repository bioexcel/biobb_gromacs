#!/usr/bin/env python3

"""Module containing the Convert_tpr class and the command line interface."""
from typing import Optional
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools.file_utils import launchlogger
from biobb_gromacs.gromacs.common import get_gromacs_version


class ConvertTpr(BiobbObject):
    """
    | biobb_gromacs ConvertTpr
    | Wrapper of the `GROMACS convert-tpr <https://manual.gromacs.org/current/onlinehelp/gmx-convert-tpr.html>`_ module.
    | The GROMACS convert-tpr module can edit run input files (.tpr)

    Args:
        input_tpr_path (str): Path to the input portable binary run file TPR. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_grompp.tpr>`_. Accepted formats: tpr (edam:format_2333).
        output_tpr_path (str): Path to the output portable binary run file TPR. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs/ref_grompp.tpr>`_. Accepted formats: tpr (edam:format_2333).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **extend** (*int*) - (0) Extend the runtime by this amount (ps).
            * **until** (*int*) - (0) Extend the runtime until this ending time (ps).
            * **nsteps** (*int*) - (0) Change the number of steps remaining to be made.
            * **gmx_lib** (*str*) - (None) Path set GROMACS GMXLIB environment variable.
            * **binary_path** (*str*) - ("gmx") Path to the GROMACS executable binary.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.
            * **container_path** (*str*) - (None)  Path to the binary executable of your container.
            * **container_image** (*str*) - ("gromacs/gromacs:latest") Container Image identifier.
            * **container_volume_path** (*str*) - ("/data") Path to an internal directory in the container.
            * **container_working_dir** (*str*) - (None) Path to the internal CWD in the container.
            * **container_user_id** (*str*) - (None) User number id to be mapped inside the container.
            * **container_shell_path** (*str*) - ("/bin/bash") Path to the binary executable of the container shell.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_gromacs.gromacs.convert_tpr import convert_tpr

            prop = { 'extend': 100000}
            convert_tpr(input_tpr_path='/path/to/myStructure.tpr',
                   output_tpr_path='/path/to/newCompiledBin.tpr',
                   properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS Convert-tpr
            * version: 2025.2
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_tpr_path: str, output_tpr_path: str,
                 properties: Optional[dict] = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_tpr_path": input_tpr_path},
            "out": {"output_tpr_path": output_tpr_path}
        }

        # Properties specific for BB
        self.extend = properties.get('extend')
        self.until = properties.get('until')
        self.nsteps = properties.get('nsteps')

        # Properties common in all GROMACS BB
        self.gmx_lib = properties.get('gmx_lib', None)
        self.binary_path = properties.get('binary_path', 'gmx')
        self.gmx_nobackup = properties.get('gmx_nobackup', True)
        self.gmx_nocopyright = properties.get('gmx_nocopyright', True)
        if self.gmx_nobackup:
            self.binary_path += ' -nobackup'
        if self.gmx_nocopyright:
            self.binary_path += ' -nocopyright'
        if not self.container_path:
            self.gmx_version = get_gromacs_version(self.binary_path)

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`ConvertTpr <gromacs.convert_tpr.ConvertTpr>` object."""

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        self.cmd = [self.binary_path, 'convert-tpr',
                    '-s', self.stage_io_dict["in"]["input_tpr_path"],
                    '-o', self.stage_io_dict["out"]["output_tpr_path"]
                    ]

        if self.extend:
            self.cmd.extend(['-extend', str(self.extend)])
        if self.until:
            self.cmd.extend(['-until', str(self.until)])
        if self.nsteps:
            self.cmd.extend(['-nsteps', str(self.nsteps)])

        if self.gmx_lib:
            self.env_vars_dict['GMXLIB'] = self.gmx_lib

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)
        return self.return_code


def convert_tpr(input_tpr_path: str, output_tpr_path: str, properties: Optional[dict] = None, **kwargs) -> int:
    """Create :class:`ConvertTpr <gromacs.convert_tpr.ConvertTpr>` class and
    execute the :meth:`launch() <gromacs.convert_tpr.ConvertTpr.launch>` method."""
    return ConvertTpr(**dict(locals())).launch()


convert_tpr.__doc__ = ConvertTpr.__doc__
main = ConvertTpr.get_main(
    convert_tpr, "Wrapper of the GROMACS convert-tpr module.")


if __name__ == '__main__':
    main()
