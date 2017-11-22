#!F:\python\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'flask==0.11.1','console_scripts','flask'
__requires__ = 'flask==0.11.1'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('flask==0.11.1', 'console_scripts', 'flask')()
    )
