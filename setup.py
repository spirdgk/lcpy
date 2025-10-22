from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext as _build_ext


class build_ext(_build_ext): # We define a class inheriting from the build_ext class of setuptools
    def finalize_options(self): # We override the finalize_options function
        import numpy
        if self.include_dirs is None: # If the list that holds the directories to be included is empty:
            self.include_dirs = [] # we initialize an empty list
        self.include_dirs.append(numpy.get_include()) # and append numpy's C header files, which has to be available for the C compiler to work on the .pyx files
        super().finalize_options() # and we call the original function

# Here we define a list of compiled Cython extensions we want to build
ext_modules = [
    Extension( # we create an Extension object
        "lcpy.cython_files.calc",   # this is the name of the object (python import path/ module name)
        ["lcpy/cython_files/calc.pyx"], #  #This is where to get the pyx file from (physical file path to the .pyx source code)
    )
]
# The extension basically says to the setuptools and cython to compile the .pyx file to a pyd file

setup(
    name="lcpy", # name of the projetc
    version="1.0.0", # version
    packages=[ # The packages and sub-packages to include in the distribution
        "lcpy",
        "lcpy.calculators",
        "lcpy.hvs",
        "lcpy.cython_files",
    ],
    ext_modules=ext_modules,  # Here we say to the setuptools that there are extensions to build and from where to get them
    cmdclass={'build_ext': build_ext}, # Here we sepcify that to build the extensions we need to use the custom build_ext class to include the numpy C headers as needed
    setup_requires=["cython", "numpy"], # Packages to be installed before build (build-time dependencies)
    install_requires=[ # runtime dependencies
        "numpy",
        "pandas",
        "matplotlib",
        "seaborn",
        "xlsxwriter"
    ],
    extras_require = {
        "bw" = [
            "premise[bw2]",
            "brightway2==2.4.7"
        ]
    },
    python_requires=">=3.10", # python requirement
    license="BSD 3-Clause",
    zip_safe=False,
)

#>=1.21,<2.0
