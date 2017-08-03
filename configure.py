import os
import sys
import sipconfig
import sipdistutils
import PyQt5
import subprocess
import argparse

from os.path import splitext
from os.path import dirname
from glob import glob
from distutils.spawn import find_executable

from PyQt5.QtCore import PYQT_CONFIGURATION
from plio.utils.utils import find_in_dict
from PyQt5.QtCore import PYQT_CONFIGURATION as qtconfigdict
from sipconfig import ModuleMakefile

def main (module):
    # The name of the SIP build file generated by SIP and used by the build
    # system.
    sipy_sip_dir = "sipdir/"
    module = module + '.sip'
    build_file = "bundle"+".sbf"
    target = module+".so"

    # Get the extra SIP flags needed by the imported qt module.  Note that
    # this normally only includes those flags (-x and -t) that relate to SIP's
    # versioning system.
    qt_sip_flags = qtconfigdict["sip_flags"]

    # sip_bin = current_env_path + "/bin/sip"
    sip_bin = find_executable('sip')
    pyqt_sip_dir = dirname(dirname(sip_bin)) + "/share/sip/PyQt5"

    # Get the PyQt configuration information.
    config = sipconfig.Configuration()

    # Run SIP to generate the code.  Note that we tell SIP where to find the qt
    # module's specification files using the -I flag.
    os.system(" ".join([sip_bin, "-c", ".", "-b", build_file, "-I",
        pyqt_sip_dir, qt_sip_flags, sipy_sip_dir+module+".sip"]))

    # We are going to install the SIP specification file for this module and
    # its configuration module.
    installs = []
    installs.append([module+".sip", os.path.join(pyqt_sip_dir, "isis3")])

    isis_root = os.getenv("ISISROOT")
    if not isis_root:
        raise("Please set ISIS")

    extra_libs = ["$(ALLLIBS)", "-Wl,-rpath,"+isis_root+"/lib", "-Wl,-rpath,"+isis_root+"/3rdParty/lib"]

    makefile = ModuleMakefile(configuration=config, build_file=build_file, installs=installs)
    makefile.extra_cxxflags = ["$(ALLINCDIRS)", "-Wstrict-aliasing=0", "-Wno-unused-variable"]
    makefile.extra_lflags =  ["$(ALLLIBDIRS)"]
    makefile.extra_include_dirs = [x[0] for x in os.walk('incs/')]
    makefile.extra_lib_dirs = [isis_root + '/3rdParty/lib', isis_root + 'lib']
    makefile.generate()

    # add import line for isismake.os
    isis_makefile = "include " + isis_root + "/make/isismake.os"

    with open("Makefile", 'r+') as f:
        content = f.read()
        content = content.replace("LIBS =", "LIBS = " + ' '.join(extra_libs))
        f.seek(0, 0)
        f.write(isis_makefile + '\n\n' + content)

if __name__ == "__main__":
    clean = ['cpp', 'c', 'h', 'hpp', 'o', 'sbf']

    # If clean is passed in, clear up all the files genreated by the scripts
    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        files = []
        for filetype in clean:
            files.extend(glob('*.{}'.format(filetype)))

        for f in files:
            os.remove(f)
        exit()

    main('master')
