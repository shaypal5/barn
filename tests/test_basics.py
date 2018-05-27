from barn import Dataset


test_ds1 = Dataset(
    name='test1',
    task='testing',
)


def test_fname():
    some_name = test_ds1.fname()
    assert some_name.endswith('.csv')
    tag1 = 'hovercraft'
    name_with_tag = test_ds1.fname(tags=[tag1])
    assert name_with_tag.endswith('.csv')
    assert tag1 in name_with_tag
