py -m build
py -m twine upload dist/0.5/*
pip install airtouch3
pip show airtouch3