from setuptools import find_packages, setup
from setuptools.extension import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext

setup(
    name="main",
    version="0.100",
    ext_modules=cythonize(
        [
            Extension(
                "main",
                [
                    "./main.py",
                    "./cogs/almaviva_script.py",
                    "./cogs/colors.py",
                    "./cogs/Countdown.py",
                    "./cogs/customized_components.py",
                    "./cogs/gui.py",
                    "./cogs/login_gui.py",
                    "./cogs/login_manager.py",
                    "./cogs/utility.py",
                ],
            ),
        ],
        build_dir="build_cythonize",
        compiler_directives={
            "language_level": "3",
            "always_allow_keywords": True,
        },
    ),
    cmdclass=dict(build_ext=build_ext),
)
