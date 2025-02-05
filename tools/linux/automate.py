#!/usr/bin/python -u

import sys
sys.path.append('../../scripts')
import base
import os
import subprocess
import deps
import shutil
import multiprocessing

def get_branch_name(directory):
  cur_dir = os.getcwd()
  os.chdir(directory)
  # detect build_tools branch
  #command = "git branch --show-current"
  command = "git symbolic-ref --short -q HEAD"
  current_branch = base.run_command(command)['stdout']
  os.chdir(cur_dir)
  return current_branch

def install_qt():
    # qt
    if not base.is_file("./qt_source_5.9.9.tar.xz"):
        base.download("https://download.qt.io/archive/qt/5.9/5.9.9/single/qt-everywhere-opensource-src-5.9.9.tar.xz", "./qt_source_5.9.9.tar.xz")

    if not base.is_dir("./qt-everywhere-opensource-src-5.9.9"):
        base.cmd("tar", ["-xf", "./qt_source_5.9.9.tar.xz"])

    qt_params = ["-opensource",
                "-confirm-license",
                "-release",
                "-shared",
                "-accessibility",
                "-prefix",
                "./../qt_build/Qt-5.9.9/gcc_64",
                "-qt-zlib",
                "-qt-libpng",
                "-qt-libjpeg",
                "-qt-xcb",
                "-qt-pcre",
                "-no-sql-sqlite",
                "-no-qml-debug",
                "-gstreamer", "1.0",
                "-nomake", "examples",
                "-nomake", "tests",
                "-skip", "qtenginio",
                "-skip", "qtlocation",
                "-skip", "qtserialport",
                "-skip", "qtsensors",
                "-skip", "qtxmlpatterns",
                "-skip", "qt3d",
                "-skip", "qtwebview",
                "-skip", "qtwebengine"]

    base.cmd_in_dir("./qt-everywhere-opensource-src-5.9.9", "./configure", qt_params)
    base.cmd_in_dir("./qt-everywhere-opensource-src-5.9.9", "make", [
        "-j",
        str(multiprocessing.cpu_count())
    ])
    base.cmd_in_dir("./qt-everywhere-opensource-src-5.9.9", "make", ["install"])
    shutil.rmtree("/build_tools/tools/linux/qt-everywhere-opensource-src-5.9.9")
    os.remove("/build_tools/tools/linux/qt_source_5.9.9.tar.xz")
    return

branch = get_branch_name("../..")

array_args = sys.argv[1:]
array_modules = []
params = []

config = {}
for arg in array_args:
    if (0 == arg.find("--")):
        indexEq = arg.find("=")
        if (-1 != indexEq):
            config[arg[2:indexEq]] = arg[indexEq + 1:]
            params.append(arg[:indexEq])
            params.append(arg[indexEq + 1:])
    else:
        array_modules.append(arg)

branch = config["branch"] if "branch" in config else "None"
modules = " ".join(array_modules) if " ".join(array_modules) != "" else "desktop builder server"

platformm = config["platform"]

print(
    "-" * 46 +
    "\nbuild branch: " + branch + "\n" +
    "build modules: " + modules + "\n" +
    "platform: " + platformm + "\n" +
    "-" * 46
)

if not base.is_file("./node_js_setup_10.x"):
    print("install dependencies...")
    deps.install_deps()

if not base.is_dir("./qt_build"):
    print("install qt...")
    install_qt()

build_tools_params = ["--branch", branch, 
                    "--module", modules, 
                    "--update", "1",
                    "--qt-dir", os.getcwd() + "/qt_build/Qt-5.9.9"] + params

base.cmd_in_dir("../..", "./configure.py", build_tools_params)
base.cmd_in_dir("../..", "./make.py")
