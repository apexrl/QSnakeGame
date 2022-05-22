import os
import sys
import subprocess

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: "
                + ", ".join(e.name for e in self.extensions)
            )
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = [
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + extdir,
            "-DPYTHON_EXECUTABLE=" + sys.executable,
            '-DVERSION="' + self.distribution.get_version() + '"',
        ]
        build_args = ["--", "-j2"]

        env = os.environ.copy()

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env
        )
        subprocess.check_call(
            ["cmake", "--build", ".", "--target", "snake_env_cpp"] + build_args,
            cwd=self.build_temp,
        )


setup(
    name="SnakeEnv",
    version="1.0",
    author="Jingxiao Chen, Zhengbang Zhu",
    ext_modules=[CMakeExtension("snake_env_cpp")],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "scipy",
        "pygame",
        "numpy",
        "pytest",
    ]
)
