#! /bin/sh

# 1) Run translate1.sh
# 2) Edit the .po files, translating strings
# 3) Run translate2.sh to compile the translations
# 4) Test

echo
# python2.7 ./setup.py extract_messages
pybabel extract -k tr --omit-header --sort-by-file -F deform_bootstrap_extra/locale/main_mapping.conf -o deform_bootstrap_extra/locale/deform_bootstrap_extra.pot deform_bootstrap_extra
echo
./setup.py update_catalog
