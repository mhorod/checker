"""
Install requirements and setup the application
"""
import subprocess
import sys


def install(package):
    """Install package"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


external_packages = ['termcolor', 'console_progressbar']
for package_name in external_packages:
    install(package_name)
