# -*- coding: utf-8 -*-
import os

import pytest

from pyramid_oereb.lib.adapter import FileAdapter


def test_init():
    base_path = os.path.abspath('.')
    file_adapter_1 = FileAdapter()
    assert file_adapter_1.cwd == base_path
    file_adapter_2 = FileAdapter('test')
    assert file_adapter_2.cwd == os.path.join(base_path, 'test')


def test_cd():
    base_path = os.path.abspath('.')
    file_adapter = FileAdapter()
    file_adapter.cd('test')
    assert file_adapter.cwd == os.path.join(base_path, 'test')


def test_ls():
    base_path = os.path.abspath('./tests/resources')
    file_adapter = FileAdapter(base_path)
    dir_list = file_adapter.ls()
    assert isinstance(dir_list, list)
    assert len(dir_list) == 12
    file_found = False
    dir_found = False
    for entry in dir_list:
        if entry[0] == 'test_config.yml':
            file_found = True
            assert entry[1].get('is_file')
            assert not entry[1].get('is_dir')
        if entry[0] == 'schema':
            dir_found = True
            assert not entry[1].get('is_file')
            assert entry[1].get('is_dir')
    assert file_found and dir_found


def test_read():
    base_path = os.path.abspath('./tests/resources')
    file_adapter = FileAdapter(base_path)
    content = file_adapter.read('file_adapter_dummy.txt').decode('utf-8')
    assert content.startswith('If the content looks like this, the test has been successful.')


def test_read_no_file():
    base_path = os.path.abspath('./tests/resources')
    file_adapter = FileAdapter(base_path)
    with pytest.raises(IOError) as exc_info:
        file_adapter.read('plr119')
    assert 'Not a file:' in str(exc_info.value)
