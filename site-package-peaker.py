import glob
import os
import sys

# Specify the path to your site-packages directory
python_prefix = sys.prefix
site_packages_path = os.path.join(python_prefix, "Lib", "site-packages")


print(site_packages_path)

# Use glob to list all files and directories in site-packages
libraries = [
    os.path.basename(path) for path in glob.glob(os.path.join(site_packages_path, "*"))
]

# Print the list of library names
for library in libraries:
    print(library)
