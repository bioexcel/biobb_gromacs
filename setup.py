import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="biobb_gromacs",
    version="3.8.1",
    author="Biobb developers",
    author_email="pau.andrio@bsc.es",
    description="biobb_gromacs is the Biobb module collection to perform molecular dynamics simulations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="Bioinformatics Workflows BioExcel Compatibility",
    url="https://github.com/bioexcel/biobb_gromacs",
    project_urls={
        "Documentation": "http://biobb_gromacs.readthedocs.io/en/latest/",
        "Bioexcel": "https://bioexcel.eu/"
    },
    packages=setuptools.find_packages(exclude=['docs', 'test']),
    install_requires=['biobb_common==3.8.1'],
    python_requires='>=3.7',
    entry_points={
        "console_scripts": [
            "editconf = biobb_gromacs.gromacs.editconf:main",
            "genion = biobb_gromacs.gromacs.genion:main",
            "genrestr = biobb_gromacs.gromacs.genrestr:main",
            "grompp = biobb_gromacs.gromacs.grompp:main",
            "make_ndx = biobb_gromacs.gromacs.make_ndx:main",
            "gmxselect = biobb_gromacs.gromacs.gmxselect:main",
            "mdrun = biobb_gromacs.gromacs.mdrun:main",
            "grompp_mdrun = biobb_gromacs.gromacs.grompp_mdrun:main",
            "pdb2gmx = biobb_gromacs.gromacs.pdb2gmx:main",
            "solvate = biobb_gromacs.gromacs.solvate:main",
            "trjcat = biobb_gromacs.gromacs.trjcat:main",
            "ndx2resttop = biobb_gromacs.gromacs_extra.ndx2resttop:main",
            "append_ligand = biobb_gromacs.gromacs_extra.append_ligand:main"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX"
    ],
)
