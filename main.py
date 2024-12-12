from importlib import reload
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import interface
reload(interface)

def run():
    interface.main()
