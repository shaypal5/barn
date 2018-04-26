"""Remote dataset storage on Azure."""

import os
import ntpath
import warnings

from decore import lazy_property
try:
    from azure.storage.blob import BlockBlobService
except ImportError:
    warnings.warn(
        "Importing azure Python package failed. "
        "Azure-based remote dataset stores are disabled.")

from .cfg import (
    BARN_CFG,
    _snail_case,
)
from .exceptions import (
    MissingDatasetError,
)


# ENDPOINT_TEMPLATE = 'https://{}.blob.core.windows.net/'
#
#
# def _service_endpoint_by_account_name(account_name):
#     return ENDPOINT_TEMPLATE.format(account_name)
#
#
# @lazy_property
# def _dataset_service_endpoint():
#     return _service_endpoint_by_account_name(
#         BARN_CFG['azure']['account_name'])
#
#
# def _dataset_blob_uri(file_name):
#     return '{}/{}/{}'.format(
#         _dataset_service_endpoint(),
#         BARN_CFG['azure']['container_name'],
#         file_name,
#     )


@lazy_property
def _blob_service():
    return BlockBlobService(
        account_name=BARN_CFG['azure']['account_name'],
        account_key=BARN_CFG['azure']['account_key'],
        socket_timeout=600,
    )


def _subfolder_name(dataset_name):
    t = dataset_name.lower()
    t = t.replace(' ', '_')
    return t


def _blob_name(dataset_name, file_name, task=None, dataset_attributes=None):
    path_prefix = 'barn'
    if task:
        path_prefix += '/{}'.format(_snail_case(task))
    if dataset_attributes:
        for k, v in sorted(dataset_attributes.items()):
            path_prefix += '/{}_{}'.format(_snail_case(k), _snail_case(v))
    subfolder = _subfolder_name(dataset_name=dataset_name)
    path_prefix += '/{}'.format(subfolder)
    return '{}/{}'.format(path_prefix, file_name)


def upload_dataset(
        dataset_name, file_path, task=None, dataset_attributes=None, **kwargs):
    """Uploads the given file to dataset store.

    Parameters
    ----------
    dataset_name : str
        The name of the dataset to upload.
    file_path : str
        The full path to the file to upload
    task : str, optional
        The task for which the given dataset is used for. If not given, a path
        for the corresponding task-agnostic directory is used.
    dataset_attributes : dict, optional
        Additional attributes of the datasets. Used to generate additional
        sub-folders on the blob "path". For example, providing 'lang=en' will
        results in a path such as '/lang_en/mydataset.csv'. Hierarchy always
        matches lexicographical order of keyword argument names, so 'lang=en'
        and 'animal=dog' will result in a path such as
        'task_name/animal_dof/lang_en/dset.csv'.
    **kwargs : extra keyword arguments
        Extra keyword arguments are forwarded to
        azure.storage.blob.BlockBlobService.create_blob_from_path.
    """
    fname = ntpath.basename(file_path)
    blob_name = _blob_name(
        dataset_name=dataset_name,
        file_name=fname,
        task=task,
        dataset_attributes=dataset_attributes,
    )
    print(blob_name)
    _blob_service().create_blob_from_path(
        container_name=BARN_CFG['azure']['container_name'],
        blob_name=blob_name,
        file_path=file_path,
        **kwargs,
    )


def download_dataset(
        dataset_name, file_path, task=None, dataset_attributes=None, **kwargs):
    """Uploads the given dataset from dataset store.

    Parameters
    ----------
    dataset_name : str
        The name of the dataset to upload.
    file_path : str
        The full path to the file to upload
    task : str, optional
        The task for which the given dataset is used for. If not given, a path
        for the corresponding task-agnostic directory is used.
    dataset_attributes : dict, optional
        Additional attributes of the datasets. Used to generate additional
        sub-folders on the blob "path". For example, providing 'lang=en' will
        results in a path such as '/lang_en/mydataset.csv'. Hierarchy always
        matches lexicographical order of keyword argument names, so 'lang=en'
        and 'animal=dog' will result in a path such as
        'task_name/animal_dof/lang_en/dset.csv'.
    **kwargs : extra keyword arguments
        Extra keyword arguments are forwarded to
        azure.storage.blob.BlockBlobService.get_blob_to_path.
    """
    fname = ntpath.basename(file_path)
    blob_name = _blob_name(
        dataset_name=dataset_name,
        file_name=fname,
        task=task,
        dataset_attributes=dataset_attributes,
    )
    # print("Downloading blob: {}".format(blob_name))
    try:
        _blob_service().get_blob_to_path(
            container_name=BARN_CFG['azure']['container_name'],
            blob_name=blob_name,
            file_path=file_path,
            **kwargs,
        )
    except Exception as e:
        if os.path.isfile(file_path):
            os.remove(file_path)
        raise MissingDatasetError(
            "With blob {}.".format(blob_name)) from e
