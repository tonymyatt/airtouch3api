py -m build
py -m twine upload dist/0.3/*
pip install airtouch3
pip show airtouch3