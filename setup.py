from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

setup(
    name="Freqscout",
    version="0.1.0",
    ext_modules=[
        Pybind11Extension(
            "tmh_pybind",
            ["cpp/tmh_pybind.cpp"],
            include_dirs=["cpp/treeminhash/c++"],   
            cxx_std=17,
            extra_compile_args=["-O3"],
        )
    ],
    cmdclass={"build_ext": build_ext},
    packages=[],
    py_modules=[],
)