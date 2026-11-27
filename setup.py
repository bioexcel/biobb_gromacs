import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="biobb_gromacs",
    version="5.3.2",
    author="Biobb developers",
    author_email="pau.andrio@bsc.es",
    description="biobb_gromacs is the Biobb module collection to perform molecular dynamics simulations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="Bioinformatics Workflows BioExcel Compatibility",
    url="https://github.com/bioexcel/biobb_gromacs",
    project_urls={
        "Documentation": "http://biobb-gromacs.readthedocs.io/en/latest/",
        "Bioexcel": "https://bioexcel.eu/",
    },
    packages=setuptools.find_packages(exclude=["docs", "test"]),
    package_data={"biobb_gromacs": ["py.typed"]},
    install_requires=["biobb_common==5.3.1"],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "convert_tpr = biobb_gromacs.gromacs.convert_tpr:ConvertTpr.main",
            "editconf = biobb_gromacs.gromacs.editconf:Editconf.main",
            "genion = biobb_gromacs.gromacs.genion:Genion.main",
            "genrestr = biobb_gromacs.gromacs.genrestr:Genrestr.main",
            "grompp = biobb_gromacs.gromacs.grompp:Grompp.main",
            "make_ndx = biobb_gromacs.gromacs.make_ndx:MakeNdx.main",
            "gmxselect = biobb_gromacs.gromacs.gmxselect:Gmxselect.main",
            "mdrun = biobb_gromacs.gromacs.mdrun:Mdrun.main",
            "mdrun_plumed = biobb_gromacs.gromacs.mdrun_plumed:MdrunPlumed.main",
            "mdrun_multidir = biobb_gromacs.gromacs.mdrun_multidir:MdrunMultidir.main",
            "grompp_mdrun = biobb_gromacs.gromacs.grompp_mdrun:GromppMdrun.main",
            "pdb2gmx = biobb_gromacs.gromacs.pdb2gmx:Pdb2gmx.main",
            "insert_molecules = biobb_gromacs.gromacs.insert_molecules:InsertMolecules.main",
            "solvate = biobb_gromacs.gromacs.solvate:Solvate.main",
            "trjcat = biobb_gromacs.gromacs.trjcat:Trjcat.main",
            "ndx2resttop = biobb_gromacs.gromacs_extra.ndx2resttop:Ndx2resttop.main",
            "append_ligand = biobb_gromacs.gromacs_extra.append_ligand:AppendLigand.main",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix",
    ],
)
