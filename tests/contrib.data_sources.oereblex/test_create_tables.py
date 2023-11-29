import pytest
import sys


def test_call_no_args():
    from pyramid_oereb.contrib.data_sources.oereblex.create_tables import create_oereblex_tables
    sys.argv = []
    with pytest.raises(IndexError):
        create_oereblex_tables()


def test_call_config_missing():
    from pyramid_oereb.contrib.data_sources.oereblex.create_tables import create_oereblex_tables
    sys.argv = ["-h"]
    with pytest.raises(SystemExit):
        create_oereblex_tables()


def test_call_help():
    from pyramid_oereb.contrib.data_sources.oereblex.create_tables import create_oereblex_tables
    sys.argv = [
        # first element int array is always the script path,
        # we can leave empty because we fake the syscall
        # directly in python
        "",
        "-h"
    ]
    with pytest.raises(SystemExit) as code:
        create_oereblex_tables()
    # means script exited correctly
    assert code.value.code == 0
