#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment, CMake
import os


class YASMInstallerConan(ConanFile):
    name = "yasm_installer"
    version = "1.3.0"
    url = "https://github.com/bincrafters/conan-yasm_installer"
    description = "Yasm is a complete rewrite of the NASM assembler under the “new” BSD License"
    license = "BSD"
    exports_sources = ["LICENSE"]
    settings = "os_build", "arch_build", "compiler"
    _source_subfolder = "sources"
    generators = "cmake"

    def source(self):
        source_url = "http://www.tortall.net/projects/yasm/releases/yasm-%s.tar.gz" % self.version
        tools.get(source_url)
        extracted_dir = 'yasm-%s' % self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.download('https://raw.githubusercontent.com/yasm/yasm/master/YASM-VERSION-GEN.bat',
                       os.path.join('sources', 'YASM-VERSION-GEN.bat'))

    def build(self):
        if self.settings.os_build == 'Windows':
            self._build_cmake()
        else:
            self._build_configure()

    def _build_cmake(self):
        cmake = CMake(self, build_type='Release')
        cmake.configure(source_folder='sources')
        cmake.build(args=['--config', 'Release'])

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            cc = os.environ.get('CC', 'gcc')
            cxx = os.environ.get('CXX', 'g++')
            if self.settings.arch_build == 'x86':
                cc += ' -m32'
                cxx += ' -m32'
            elif self.settings.arch_build == 'x86_64':
                cc += ' -m64'
                cxx += ' -m64'
            env_build = AutoToolsBuildEnvironment(self)
            env_build_vars = env_build.vars
            env_build_vars.update({'CC': cc, 'CXX': cxx})
            env_build.configure(vars=env_build_vars)
            env_build.make(vars=env_build_vars)
            env_build.install(vars=env_build_vars)

    def package(self):
        self.copy(pattern="BSD.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.os_build == 'Windows':
            self.copy(pattern='*.exe', src='Release', dst='bin', keep_path=False)
            self.copy(pattern='*.dll', src='Release', dst='bin', keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, 'bin'))

    def package_id(self):
        del self.info.settings.compiler
