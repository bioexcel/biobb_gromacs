#!/usr/bin/env python3

"""Module containing the Ndx2resttop class and the command line interface."""
import fnmatch
from typing import Optional
from typing import Any
from pathlib import Path
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger


class Ndx2resttop(BiobbObject):
    """
    | biobb_gromacs Ndx2resttop
    | Generate a restrained topology from an index NDX file.
    | This module automatizes the process of restrained topology generation starting from an index NDX file.

    Args:
        input_ndx_path (str): Path to the input NDX index file. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs_extra/ndx2resttop.ndx>`_. Accepted formats: ndx (edam:format_2033).
        input_top_zip_path (str): Path the input TOP topology in zip format. File type: input. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/data/gromacs_extra/ndx2resttop.zip>`_. Accepted formats: zip (edam:format_3987).
        output_top_zip_path (str): Path the output TOP topology in zip format. File type: output. `Sample file <https://github.com/bioexcel/biobb_gromacs/raw/master/biobb_gromacs/test/reference/gromacs_extra/ref_ndx2resttop.zip>`_. Accepted formats: zip (edam:format_3987).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **posres_names** (*str*) - ("CUSTOM_POSRES") Space-separated preprocessor macro names, one per triplet (e.g. ``"CHAIN_A_POSRES CHAIN_B_POSRES"``). Activated at grompp time via ``-D <name>``. Must match the length of ref_rest_mol_triplet_list.
            * **force_constants** (*str*) - ("500 500 500") Three space-separated force constants Fx Fy Fz in kJ/mol/nm². Written verbatim into each ITP line so the same value is applied to every restrained atom.
            * **ref_rest_mol_triplet_list** (*str*) - (None) Comma-separated triplets ``(reference_group, restrain_group, molecule_name)``, one per molecule to restrain.``reference_group``: NDX group containing *all* atoms of the molecule in global (system-wide) GROMACS numbering. Used only as a coordinate frame to convert global indices to molecule-local 1-based indices. Example: ``r_1-9280``. ``restrain_group``: NDX group with the subset of atoms to actually restrain (must be a strict subset of reference_group). Example: ``P_&_r_1-9280``. ``molecule_name``: the ``[ moleculetype ]`` name in the topology used to locate where to splice the ``#ifdef`` block. Example: ``1TSR``.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_gromacs.gromacs_extra.ndx2resttop import ndx2resttop
            prop = { 'ref_rest_mol_triplet_list': '( Chain_A, Chain_A_noMut, Protein_chain_A ), ( Chain_B, Chain_B_noMut, Protein_chain_B ), ( Chain_C, Chain_C_noMut, Protein_chain_C ), ( Chain_D, Chain_D_noMut, Protein_chain_D )' }
            ndx2resttop(input_ndx_path='/path/to/myIndex.ndx',
                        input_top_zip_path='/path/to/myTopology.zip',
                        output_top_zip_path='/path/to/newTopology.zip',
                        properties=prop)

    Info:
        * wrapped_software:
            * name: In house
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(self, input_ndx_path: str, input_top_zip_path: str, output_top_zip_path: str,
                 properties: Optional[dict] = None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_ndx_path": input_ndx_path, "input_top_zip_path": input_top_zip_path},
            "out": {"output_top_zip_path": output_top_zip_path}
        }

        # Properties specific for BB
        self.posres_names = properties.get('posres_names')
        self.force_constants = properties.get('force_constants', '500 500 500')
        self.ref_rest_mol_triplet_list = properties.get('ref_rest_mol_triplet_list')

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    # --- Private helpers ---

    def _parse_ndx_groups(self, ndx_lines: list) -> dict:
        """Parse a GROMACS NDX file into a lookup table of group line ranges.

        NDX format: each named group starts with a ``[ group_name ]`` header line,
        followed by one or more rows of whitespace-separated global atom indices.

        Returns a dict mapping the raw header string (e.g. ``'[ System ]'``) to a
        two-element list ``[start_line, end_line]`` where the range is **half-open**
        (matching Python slice semantics): ``ndx_lines[start_line:end_line]`` yields
        the data rows for that group (the header line itself at ``start_line - 1`` is
        excluded).

        Edge cases handled:

        - **Last group**: the final group has no successor header to trigger the end
          assignment, so it is closed explicitly with ``index + 1`` (not ``index``)
          to include the very last data line.
        - **Single-content-line groups**: when a header is immediately followed by
          another header (no trailing blank line), the default range would be
          ``[H, H+1]`` giving an empty slice. The post-loop fix increments end by 1
          to capture that single data line.
        """
        groups_dic: dict[str, Any] = {}
        current_group = ''
        previous_group = ''

        for index, line in enumerate(ndx_lines):
            if line.startswith('['):
                current_group = line
                groups_dic[current_group] = [index, 0]
                if previous_group:
                    groups_dic[previous_group][1] = index
                previous_group = current_group

            if index == len(ndx_lines) - 1:
                groups_dic[current_group][1] = index + 1

        # Fix single-content-line groups
        for group_name in groups_dic:
            if groups_dic[group_name][0] + 1 == groups_dic[group_name][1]:
                groups_dic[group_name][1] += 1

        return groups_dic

    def _read_ndx_atoms(self, ndx_lines: list, groups_dic: dict, group_name: str) -> list:
        """Return the flat list of global atom indices for a named NDX group.

        Slices the group's data rows from ndx_lines using the half-open range
        stored in groups_dic, then flattens all whitespace-separated tokens into
        a single list of integers.

        Returned integers are **global** (system-wide) GROMACS atom numbers, 1-based.
        """
        key = f'[ {group_name} ]'
        start = groups_dic[key][0] + 1
        stop  = groups_dic[key][1]
        fu.log(f'{group_name}: start_closed={start} stop_open={stop}', self.out_log, self.global_log)
        atoms = [int(atom) for line in ndx_lines[start:stop] for atom in line.split()]
        return atoms

    def _write_posre_itp(self, itp_path: str, selected_atoms: list) -> None:
        """Write a GROMACS position restraint ITP file.

        ``selected_atoms`` must contain **molecule-local** 1-based atom indices
        (not global system-wide indices). The atom type column is hardcoded to
        ``1`` (GROMACS position restraint type). ``self.force_constants`` is a
        verbatim string ``"Fx Fy Fz"`` applied uniformly to every restrained atom.
        """
        with open(itp_path, 'w') as f:
            fu.log(f'Creating {itp_path} with selected atoms and force constants', self.out_log, self.global_log)
            f.write('[ position_restraints ]\n')
            f.write('; atom  type      fx      fy      fz\n')
            for atom in selected_atoms:
                f.write(f'{atom}     1  {self.force_constants}\n')

    def _insert_posres_in_top(self, top_file: str, molecule_name: str, posre_name: str, itp_name: str) -> None:
        """Splice the #ifdef posres block into the .top file for single-chain topologies.

        Uses a two-phase scan over the topology lines:

        Phase 1 – locate the target moleculetype:
          For each ``[ moleculetype ]`` directive, read the first non-comment
          content line and compare its first token against ``molecule_name``.
          Set ``found_molecule = True`` when matched.

        Phase 2 – find the insertion point (only after found_molecule):
          Scan forward for the earliest of:
          - another top-level section (``[ moleculetype ]``, ``[ system ]``,
            ``[ molecules ]``)
          - an existing ``#include`` or ``#ifdef POSRES`` line
          Insert immediately before that line. Fall back to EOF if none found.

        Important: the insertion-point check (Phase 2) runs *before* the
        ``[ moleculetype ]`` detector within the same loop iteration. Without this
        ordering, a new ``[ moleculetype ]`` that should trigger insertion would
        instead be consumed by the ``continue`` in the detector, causing the block
        to be placed in the wrong molecule section.
        """
        with open(top_file, 'r') as f:
            lines = f.readlines()

        in_moleculetype = False
        found_molecule  = False
        index = None

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Find insertion point: just before the next top-level section or existing restraint block
            if found_molecule:
                is_next_section = stripped.startswith('[') and (
                    'system' in stripped or 'molecules' in stripped or 'moleculetype' in stripped)
                if is_next_section or line.startswith('#include ') or line.startswith('#ifdef POSRES'):
                    index = i
                    break

            # Detect [ moleculetype ] directive
            if stripped.startswith('[') and 'moleculetype' in stripped:
                in_moleculetype = True
                continue

            # Find the molecule name line inside the [ moleculetype ] block
            if in_moleculetype:
                if stripped and not stripped.startswith(';'):
                    in_moleculetype = False
                    if not stripped.startswith('[') and stripped.split()[0] == molecule_name:
                        found_molecule = True

        if not found_molecule:
            raise ValueError(f"Molecule type '{molecule_name}' not found in the topology file")

        if index is None:
            index = len(lines)

        lines.insert(index,     '\n')
        lines.insert(index + 1, '; Include Position restraint file\n')
        lines.insert(index + 2, f'#ifdef {posre_name}\n')
        lines.insert(index + 3, f'#include "{itp_name}"\n')
        lines.insert(index + 4, '#endif\n')
        lines.insert(index + 5, '\n')

        with open(top_file, 'w') as f:
            f.writelines(lines)

    # --- Main entry point ---

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Ndx2resttop <gromacs_extra.ndx2resttop.Ndx2resttop>` object."""
        if self.check_restart():
            return 0

        top_file = fu.unzip_top(zip_file=self.io_dict['in'].get("input_top_zip_path", ""), out_log=self.out_log, unique_dir=self.stage_io_dict.get("unique_dir", ""))

        ndx_lines = open(self.io_dict['in'].get("input_ndx_path", "")).read().splitlines()
        groups_dic = self._parse_ndx_groups(ndx_lines)
        fu.log(f'Parsed NDX groups: {list(groups_dic.keys())}', self.out_log, self.global_log)

        # Parse triplet string: "(ref, restrain, mol), ..." -> list of 3-tuples
        raw_triplets = str(self.ref_rest_mol_triplet_list).split('),')
        self.ref_rest_mol_triplet_list = [
            tuple(elem.strip(' ()').replace(' ', '').split(','))
            for elem in raw_triplets
        ]
        fu.log('ref_rest_mol_triplet_list: ' + str(self.ref_rest_mol_triplet_list), self.out_log, self.global_log)

        if self.posres_names:
            self.posres_names = [elem.strip() for elem in self.posres_names.split()]
        else:
            self.posres_names = ['CUSTOM_POSRES'] * len(self.ref_rest_mol_triplet_list)
        fu.log('posres_names: ' + str(self.posres_names), self.out_log, self.global_log)

        if len(self.posres_names) != len(self.ref_rest_mol_triplet_list):
            raise ValueError("posres_names length must match ref_rest_mol_triplet_list length")

        for triplet, posre_name in zip(self.ref_rest_mol_triplet_list, self.posres_names):
            # Per-triplet workflow:
            #   1. Unpack (reference_group, restrain_group, molecule_name)
            #   2. Read global NDX indices for both groups
            #   3. Remap restrain atoms to molecule-local 1-based indices
            #   4. Write the _posre.itp
            #   5. Inject #ifdef guard — multi-chain (per-chain .itp) or single-chain (.top)

            reference_group, restrain_group, molecule_name = triplet
            fu.log(f'Reference group: {reference_group}', self.out_log, self.global_log)
            fu.log(f'Restrain group: {restrain_group}', self.out_log, self.global_log)
            fu.log(f'Molecule name: {molecule_name}', self.out_log, self.global_log)

            itp_path = fu.create_name(path=str(Path(top_file).parent), prefix=self.prefix,
                                      step=self.step, name=restrain_group + '_posre.itp')
            self.io_dict['out']["output_itp_path"] = itp_path

            # Map global NDX indices -> molecule-local 1-based indices.
            # reference_atoms.index(atom) gives the 0-based position of each global
            # restrain atom within the reference group list. Adding 1 converts to
            # GROMACS 1-based local numbering, which matches the atom order in the
            # [ atoms ] section of each moleculetype block.
            reference_atoms = self._read_ndx_atoms(ndx_lines, groups_dic, reference_group)
            restrain_atoms  = self._read_ndx_atoms(ndx_lines, groups_dic, restrain_group)
            selected_atoms  = [reference_atoms.index(atom) + 1 for atom in restrain_atoms]

            self._write_posre_itp(itp_path, selected_atoms)
            itp_name = Path(itp_path).name

            # Multi-chain: append ifdef block to the matching per-chain ITP.
            # Detection heuristic: if any .itp file in the topology directory has
            # molecule_name in its filename (and is not already a posre/pr file),
            # this is a multi-chain topology where each chain has its own .itp
            # included by the .top. In that case, append directly to that file.
            # Otherwise fall through to single-chain mode (_insert_posres_in_top).
            multi_chain = False
            for file_dir in Path(top_file).parent.iterdir():
                if "posre" not in file_dir.name and not file_dir.name.endswith("_pr.itp"):
                    match = fnmatch.fnmatch(str(file_dir), "*" + molecule_name + "*.itp")
                    if match:
                        multi_chain = True
                        with open(str(file_dir), 'a') as f:
                            fu.log(f'Opening {file_dir} and adding ifdef include', self.out_log, self.global_log)
                            f.write('\n')
                            f.write('; Include Position restraint file\n')
                            f.write(f'#ifdef {posre_name}\n')
                            f.write(f'#include "{itp_name}"\n')
                            f.write('#endif\n')
                            f.write('\n')

            # Single-chain: splice ifdef block into the .top file
            if not multi_chain:
                self._insert_posres_in_top(top_file, molecule_name, posre_name, itp_name)

        fu.zip_top(zip_file=self.io_dict['out'].get("output_top_zip_path", ""),
                   top_file=top_file, out_log=self.out_log, remove_original_files=self.remove_tmp)
        self.remove_tmp_files()
        self.check_arguments(output_files_created=True, raise_exception=False)
        return 0


def ndx2resttop(input_ndx_path: str, input_top_zip_path: str, output_top_zip_path: str,
                properties: Optional[dict] = None, **kwargs) -> int:
    """Create :class:`Ndx2resttop <gromacs_extra.ndx2resttop.Ndx2resttop>` class and
    execute the :meth:`launch() <gromacs_extra.ndx2resttop.Ndx2resttop.launch>` method."""
    return Ndx2resttop(**dict(locals())).launch()


ndx2resttop.__doc__ = Ndx2resttop.__doc__
main = Ndx2resttop.get_main(ndx2resttop, "Generate a restrained topology from an index NDX file.")


if __name__ == '__main__':
    main()
