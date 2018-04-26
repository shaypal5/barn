"""Barn configuration."""

import os

from birch import Birch


BARN_CFG = Birch('barn')


def _base_dir():
    dpath = BARN_CFG['base_dir']
    if '~' in dpath:
        dpath = os.path.expanduser(dpath)
    return dpath


def _snail_case(s):
    s = s.lower()
    return s.replace(' ', '_')


def data_dirpath(task=None, **kwargs):
    """Get the path of the corresponding data directory.

    Parameters
    ----------
    task : str, optional
        The task for which datasets in the desired directory are used for. If
        not given, a path for the corresponding task-agnostic directory is
        returned.
    **kwargs : extra keyword arguments
        Extra keyword arguments, representing additional attributes of the
        datasets, are used to generate additional sub-folders on the path.
        For example, providing 'lang=en' will results in a path such as
        '/barn_base_dir/regression/lang_en/mydataset.csv'. Hierarchy always
        matches lexicographical order of keyword argument names, so 'lang=en'
        and 'animal=dog' will result in a path such as
        'barn_base_dir/task_name/animal_dof/lang_en/dset.csv'.

    Returns
    -------
    str
        The path to the desired dir.
    """
    path = _base_dir()
    if task:
        path = os.path.join(path, _snail_case(task))
    for k, v in sorted(kwargs.items()):
        subdir_name = '{}_{}'.format(_snail_case(k), _snail_case(v))
        path = os.path.join(path, subdir_name)
    os.makedirs(path, exist_ok=True)
    return path


def dataset_dirpath(dataset_name=None, task=None, **kwargs):
    """Get the path of the corresponding dataset file.

    Parameters
    ----------
    dataset_name : str, optional
        The name of the dataset. Used to define a sub-directory to contain all
        instances of the dataset. If not given, a dataset-agnostic directory
        path is returned.
    task : str, optional
        The task for which datasets in the desired path are used for. If not
        given, a path for the corresponding task-agnostic directory is
        returned.
    **kwargs : extra keyword arguments
        Extra keyword arguments, representing additional attributes of the
        datasets, are used to determine additional sub-folders on the path.
        For example, providing 'lang=en' will results in a path such as
        '/barn_base_dir/regression/lang_en/mydataset.csv'. Hierarchy always
        matches lexicographical order of keyword argument names, so 'lang=en'
        and 'animal=dog' will result in a path such as
        'barn_base_dir/task_name/animal_dof/lang_en/dset.csv'.

    Returns
    -------
    str
        The path to the desired dataset file.
    """
    dataset_dir_path = data_dirpath(task=task, **kwargs)
    if dataset_name:
        dataset_dir_name = _snail_case(dataset_name)
        dataset_dir_path = os.path.join(dataset_dir_path, dataset_dir_name)
    os.makedirs(dataset_dir_path, exist_ok=True)
    return dataset_dir_path


def dataset_filepath(filename, dataset_name=None, task=None, **kwargs):
    """Get the path of the corresponding dataset file.

    Parameters
    ----------
    filename : str
        The name of the file.
    dataset_name : str, optional
        The name of the dataset. Used to define a sub-directory to contain all
        instances of the dataset. If not given, a dataset-specific directory is
        not created.
    task : str, optional
        The task for which the dataset in the desired path is used for. If not
        given, a path for the corresponding task-agnostic directory is
        returned.
    **kwargs : extra keyword arguments
        Extra keyword arguments, representing additional attributes of the
        dataset, are used to generate additional sub-folders on the path.
        For example, providing 'lang=en' will results in a path such as
        '/barn_base_dir/regression/lang_en/mydataset.csv'. Hierarchy always
        matches lexicographical order of keyword argument names, so 'lang=en'
        and 'animal=dog' will result in a path such as
        'barn_base_dir/task_name/animal_dof/lang_en/dset.csv'.

    Returns
    -------
    str
        The path to the desired dataset file.
    """
    dataset_dir_path = dataset_dirpath(
        dataset_name=dataset_name, task=task, **kwargs)
    return os.path.join(dataset_dir_path, filename)
