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

from .cfg import BARN_CFG


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


def _blob_name(dataset_name, file_name):
    subfolder = _subfolder_name(dataset_name=dataset_name)
    return 'barn/{}/{}'.format(subfolder, file_name)


def upload_dataset(dataset_name, file_path, **kwargs):
    """Uploads the given file to dataset store.

    Parameters
    ----------
    **kwargs : extra keyword arguments
        Extra keyword arguments are forwarded to
        azure.storage.blob.BlockBlobService.create_blob_from_path.
    """
    fname = ntpath.basename(file_path)
    blob_name = _blob_name(dataset_name, fname)
    _blob_service().create_blob_from_path(
        container_name=BARN_CFG['azure']['container_name'],
        blob_name=blob_name,
        file_path=file_path,
        **kwargs,
    )


def download_dataset(dataset_name, file_path, **kwargs):
    """Uploads the given dataset from dataset store.

    Parameters
    ----------
    **kwargs : extra keyword arguments
        Extra keyword arguments are forwarded to
        azure.storage.blob.BlockBlobService.get_blob_to_path.
    """
    fname = ntpath.basename(file_path)
    blob_name = _blob_name(dataset_name, fname)
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
        raise e
