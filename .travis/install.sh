#!/bin/sh

set -eux

# Update things
pip install -U setuptools pip

case "$TEST_MODE"
in
    run_tests)
        pip install werkzeug
        python setup.py install
        ;;
    coverage)
        pip install coverage codecov
        pip install werkzeug
        python setup.py install
        ;;
    check_style)
        pip install flake8
        ;;
esac
