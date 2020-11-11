import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

external_packages = ['termcolor', 'console_progressbar']
for package in external_packages:
    install(package)
