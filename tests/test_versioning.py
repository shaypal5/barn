"""Versioning related tests."""

import os

import pytest
import pandas as pd

from barn import Dataset
from barn.exceptions import MissingDatasetError


test_ds3 = Dataset(
    name='test3_ver',
    task='testing_versioning',
)


def get_df1():
    df = pd.DataFrame(
        data=[['a', 1], ['b', 2]],
        columns=['char', 'int'],
    )
    df.index.name = 'index'
    return df


def get_df2():
    df = pd.DataFrame(
        data=[['a', 1], ['c', 3]],
        columns=['char', 'int'],
    )
    df.index.name = 'index'
    return df


def assert_identical_dfs(df1, df2):
    assert list(df1.columns) == list(df2.columns)
    assert list(df1.index) == list(df2.index)
    for i in df1.index:
        for j in df1.columns:
            assert df1.loc[i][j] == df2.loc[i][j]


def test_versioning():
    ver1 = '20180314'
    ver2 = '20180503'
    ver1_fname = test_ds3.fname(version=ver1)
    ver2_fname = test_ds3.fname(version=ver2)
    assert ver1_fname != ver2_fname
    df1 = get_df1()
    df2 = get_df2()
    test_ds3.dump_df(df=df1, version=ver1)
    ldf1 = test_ds3.df(version=ver1, index_col=df1.index.name)
    assert_identical_dfs(df1, ldf1)
    with pytest.raises(MissingDatasetError):
        ldf2 = test_ds3.df(version=ver2)
    test_ds3.dump_df(df=df2, version=ver2)
    ldf2 = test_ds3.df(version=ver2, index_col=df2.index.name)
    assert_identical_dfs(df2, ldf2)
    for v in [ver1, ver2]:
        fpath = test_ds3.fpath(version=v)
        os.remove(fpath)
