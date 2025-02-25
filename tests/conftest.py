"""
novelWriter – Test Suite Configuration
======================================

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import pytest
import shutil

from pathlib import Path

from mock import MockGuiMain
from tools import cleanProject

sys.path.insert(1, str(Path(__file__).parent.parent.absolute()))

import novelwriter  # noqa: E402

from PyQt5.QtWidgets import QMessageBox  # noqa: E402

from novelwriter.config import Config  # noqa: E402


@pytest.fixture(autouse=True)
def initQt(qtbot):
    """Ensures that the qt main thread is always available in all tests.
    """
    return


##
#  Core Test Folders
##

@pytest.fixture(scope="session")
def tmpPath():
    """A temporary folder for the test session. Path version.
    """
    theTemp = Path(__file__).parent / "temp"
    if theTemp.exists():
        shutil.rmtree(theTemp)
    theTemp.mkdir(exist_ok=True)
    return theTemp


@pytest.fixture(scope="session")
def tstPaths(tmpPath):
    """Returns an object that can provide the various paths needed for
    running tests.
    """
    class _Store:
        testDir = Path(__file__).parent
        filesDir = testDir / "files"
        refDir = testDir / "reference"
        outDir = tmpPath / "results"

    store = _Store()
    store.outDir.mkdir(exist_ok=True)

    return store


@pytest.fixture(scope="function")
def fncPath(tmpPath):
    """A temporary folder for a single test function. Path version.
    """
    fncPath = tmpPath / "function"
    if fncPath.is_dir():
        shutil.rmtree(fncPath)
    fncPath.mkdir(exist_ok=True)
    return fncPath


@pytest.fixture(scope="function")
def projPath(fncPath):
    """A temporary folder for a single test function,
    with a project folder.
    """
    prjDir = fncPath / "project"
    if prjDir.exists():
        shutil.rmtree(prjDir)
    prjDir.mkdir(exist_ok=True)
    return prjDir


##
#  novelWriter Objects
##

@pytest.fixture(scope="function")
def tmpConf(tmpPath):
    """Create a temporary novelWriter configuration object.
    """
    confFile = tmpPath / "novelwriter.conf"
    if confFile.is_file():
        confFile.unlink()
    theConf = Config()
    theConf.initConfig(tmpPath, tmpPath)
    theConf.setLastPath(tmpPath)
    theConf.guiLocale = "en_GB"
    return theConf


@pytest.fixture(scope="function")
def fncConf(fncPath):
    """Create a temporary novelWriter configuration object.
    """
    confFile = fncPath / "novelwriter.conf"
    if confFile.is_file():
        confFile.unlink()
    theConf = Config()
    theConf.initConfig(fncPath, fncPath)
    theConf.setLastPath(fncPath)
    theConf.guiLocale = "en_GB"
    return theConf


@pytest.fixture(scope="function")
def mockGUI(monkeypatch, tmpConf):
    """Create a mock instance of novelWriter's main GUI class.
    """
    monkeypatch.setattr("novelwriter.CONFIG", tmpConf)
    theGui = MockGuiMain()
    theGui.mainConf = tmpConf
    return theGui


@pytest.fixture(scope="function")
def nwGUI(qtbot, monkeypatch, fncPath, fncConf):
    """Create an instance of the novelWriter GUI.
    """
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    monkeypatch.setattr("novelwriter.CONFIG", fncConf)
    nwGUI = novelwriter.main(["--testmode", f"--config={fncPath}", f"--data={fncPath}"])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.wait(20)

    nwGUI.mainConf.setLastPath(fncPath)

    yield nwGUI

    qtbot.wait(20)
    nwGUI.closeMain()
    qtbot.wait(20)

    return


##
#  Python Objects
##

@pytest.fixture(scope="function")
def mockRnd(monkeypatch):
    """Create a mock random number generator that just counts upwards
    from 0. This one will generate status/importance flags and handles
    in a predictable sequence.
    """
    class MockRnd:

        def __init__(self):
            self.reset()

        def _rnd(self, n):
            for x in range(n):
                yield x

        def reset(self):
            gen = self._rnd(1000)
            monkeypatch.setattr("random.getrandbits", lambda *a: next(gen))

    return MockRnd()


##
#  Temp Project Folders
##

@pytest.fixture(scope="function")
def nwLipsum(tmpPath):
    """A medium sized novelWriter example project with a lot of Lorem
    Ipsum text.
    """
    tstDir = Path(__file__).parent
    srcDir = tstDir / "lipsum"
    dstDir = tmpPath / "lipsum"
    if dstDir.exists():
        shutil.rmtree(dstDir)

    shutil.copytree(srcDir, dstDir)
    cleanProject(dstDir)

    yield str(dstDir)

    if dstDir.exists():
        shutil.rmtree(dstDir)

    return


@pytest.fixture(scope="function")
def prjLipsum(tmpPath):
    """A medium sized novelWriter example project with a lot of Lorem
    Ipsum text.
    """
    tstDir = Path(__file__).parent
    srcDir = tstDir / "lipsum"
    dstDir = tmpPath / "lipsum"
    if dstDir.exists():
        shutil.rmtree(dstDir)

    shutil.copytree(srcDir, dstDir)
    cleanProject(dstDir)

    yield dstDir

    if dstDir.exists():
        shutil.rmtree(dstDir)

    return


@pytest.fixture(scope="session")
def ipsumText():
    """Return five paragraphs of Lorem Ipsum text.
    """
    thatIpsum = [(
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc maximus justo non dictum co"
        "mmodo. Curabitur lacinia tempor orci vel luctus. Phasellus porta metus eu massa luctus, e"
        "get euismod risus rhoncus. Vestibulum sed arcu nisi. Maecenas pretium facilisis velit, ve"
        "l semper lacus aliquam sit amet. Vestibulum vulputate neque ligula, rhoncus blandit turpi"
        "s consequat id. Mauris sagittis vehicula imperdiet. Duis sed nunc pretium, ornare purus v"
        "el, sodales augue. Maecenas a suscipit risus. Quisque volutpat justo eleifend est ullamco"
        "rper fermentum. Donec ullamcorper et tortor a laoreet. Nam id risus nisi. Vivamus non imp"
        "erdiet erat, sit amet imperdiet felis. Mauris vitae neque et est aliquam scelerisque non "
        "non ipsum."
    ), (
        "Nullam laoreet lorem nec malesuada vehicula. Vivamus tempus sodales lectus sed viverra. A"
        "enean lacinia sollicitudin quam, quis tempus eros suscipit id. Duis sed rutrum nisi, ut p"
        "ulvinar magna. Nam et cursus tortor. Phasellus ac odio tellus. Nullam in iaculis ipsum. V"
        "ivamus ante sem, ultricies sed varius quis, tristique nec tellus. Nullam eu urna vitae la"
        "cus hendrerit gravida. Quisque pulvinar erat ex, id efficitur velit sodales vitae. Proin "
        "vestibulum, sapien eget mattis euismod, tortor quam viverra risus, at congue mauris torto"
        "r eu nunc. Mauris pellentesque elit leo, quis eleifend sem placerat a. Vivamus iaculis du"
        "i eget tellus volutpat, ac varius nisi facilisis."
    ), (
        "Nullam a nisl magna. Praesent commodo nec diam aliquet vestibulum. In sapien velit, sodal"
        "es feugiat porta ut, rhoncus a elit. Quisque egestas nisi eu eros laoreet, quis facilisis"
        " est pretium. Nullam bibendum sed tellus nec lobortis. Duis elit massa, volutpat a lacini"
        "a a, ullamcorper in dui. Suspendisse ac laoreet dui. Curabitur elementum, tortor elementu"
        "m ultricies laoreet, nunc massa vulputate augue, vitae tincidunt nunc enim eget nisl."
    ), (
        "Pellentesque nibh urna, volutpat et feugiat porta, rutrum sed lectus. Aliquam eget risus "
        "id orci tincidunt condimentum et sit amet purus. Curabitur tincidunt odio vel ante feugia"
        "t feugiat. Proin nunc lorem, molestie a sapien et, varius elementum nunc. Donec non ferme"
        "ntum nisl. In et massa placerat, faucibus felis eu, congue nisi. Proin sed tortor non lor"
        "em mattis cursus. Vestibulum magna neque, bibendum vel nibh et, tincidunt rhoncus nisi. D"
        "uis pulvinar mi a quam rutrum maximus. Nunc sollicitudin, urna in cursus facilisis, augue"
        " neque imperdiet metus, ac finibus lorem ante id nulla. Sed maximus eleifend justo id feu"
        "giat. Cras eget diam vel est blandit tempor nec a leo. Mauris risus est, fringilla in ali"
        "quam a, sagittis vel enim. Nullam sodales id erat placerat lobortis."
    ), (
        "Integer ac gravida quam. Quisque eleifend nisl nec pretium tincidunt. Quisque sollicitudi"
        "n nisi in hendrerit scelerisque. Sed ornare nisl lacus, sit amet consectetur lectus egest"
        "as et. Vivamus nec arcu lorem. Donec rhoncus, purus a porta accumsan, nunc lectus iaculis"
        " libero, et fringilla tellus augue et velit. Integer varius felis scelerisque, vulputate "
        "tellus eu, laoreet justo. Suspendisse sit amet sem vehicula, auctor odio sed, aliquet eni"
        "m. In ac tortor sed tortor fringilla elementum. Nulla non odio at magna vulputate sceleri"
        "sque. Nam elementum diam eu rutrum scelerisque. Sed fermentum, felis quis vulputate ferme"
        "ntum, libero metus sollicitudin est, in faucibus purus nulla non dolor. Ut vitae felis po"
        "rta, feugiat nunc et, bibendum neque. Nullam nec lorem nec metus ullamcorper malesuada ut"
        " a nisl. Etiam eget tristique dui. Nulla sed mi finibus, venenatis tellus non, maximus en"
        "im."
    )]
    return thatIpsum
