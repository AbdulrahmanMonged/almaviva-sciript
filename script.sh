#!/usr/bin/bash

app_name="main"
echo "building for app = ${app_name}"

# cleanup
rm -R dist
rm -R build
rm -R "${app_name}.spec"
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

# compile
python setup.py build_ext --inplace

# bundle
pyinstaller \
    -w \
    --icon=thunder.ico \
    --onefile \
    --name "${app_name}" \
	--add-data "thunder.ico;." \
    main.py