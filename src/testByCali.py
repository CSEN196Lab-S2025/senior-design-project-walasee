from sys import platform
from importlib.machinery import SourceFileLoader
from os.path import join
import WalabotAPI as Wal

Wal.Init()
Wal.Initialize()
try:
    Wal.ConnectAny()
except:
    print('Please connect your Walabot')