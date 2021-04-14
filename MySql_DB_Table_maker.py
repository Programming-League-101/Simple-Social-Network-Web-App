import sys
import subprocess
import pkg_resources

required = {'flask_mysqldb'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

print(installed)

installedpkg = []

for n in installed:
    installedpkg.append(installed)

for n in range(len(installedpkg)):
    print(installedpkg[n])