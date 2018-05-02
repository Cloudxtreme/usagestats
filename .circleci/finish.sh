#!/bin/sh

set -eux

case "${TEST_MODE:-run_tests}"
in
    coverage)
        codecov
        ;;
esac
