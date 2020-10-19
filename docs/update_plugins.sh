cd ..
python3 -m jinjamator.jinjamator -t jinjamator/tasks/.internal/document_plugins/ -m destination_directory:./docs/source/plugins/content -vvv
cd docs
make clean
make html