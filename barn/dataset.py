"""Dataset objects."""

import os
import re
import shutil

from pdutil.serial import SerializationFormat

from .cfg import (
    _snail_case,
    dataset_dirpath,
    dataset_filepath,
)
from .exceptions import (
    MissingDatasetError,
)
from .azure import (
    upload_dataset,
    download_dataset,
)


class Dataset(object):
    """A barn dataset.

    Parameters
    ----------
    name : str
        The name of the dataset. Used mainly in printing messages.
    task : str, optional
        The data science task this dataset serves. Optional.
    default_ext : str, optional
        The default extension used for instances of this dataset. Also dictates
        the serialization format used by default by methods df(), dump_df() and
        upload_df(). Support 'csv' and 'feather' (for Feather format).
        Defaults to 'csv'.
    fname_base : str, optional
        The base of the file name for the dataset, without any file extension.
        E.g. 'myds' for 'myds.csv'. If not given, a snail_cased version of the
        dataset name is used.
    singleton : bool, default False
        If set, this dataset is assumed to be composed of a single instance,
        and as such no dataset-specific sub-directory is created.
    **kwargs : extra keyword arguments
        Extra keyword arguments, representing additional attributes of the
        dataset. E.g., 'language=en' or 'source=newspaper'.
    """

    EXT_PATTERN = r'\.([a-z]+)'

    def __init__(self, name, task=None, default_ext=None, fname_base=None,
                 singleton=False, **kwargs):
        self.name = name
        self.task = task
        if default_ext is None:
            default_ext = 'csv'
        self.default_ext = default_ext
        if fname_base is None:
            fname_base = _snail_case(name)
        self.fname_base = fname_base
        self.singleton = singleton
        self.kwargs = kwargs

    @staticmethod
    def _tags_to_str(tags=None):
        return '_'+'_'.join(sorted(tags)) if tags else ''

    def fname(self, tags=None, ext=None):
        """Returns the filename appropriate for an instance of this dataset.

        Parameters
        ----------
        tags : list of str, optional
            The tags associated with the given instance of this dataset.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.

        Returns
        -------
        str
            The appropariate filename.
        """
        if ext is None:
            ext = self.default_ext
        return '{}{}.{}'.format(
            self.fname_base,
            self._tags_to_str(tags=tags),
            ext,
        )

    def fpath(self, tags=None, ext=None):
        """Returns the filepath appropriate for an instance of this dataset.

        Parameters
        ----------
        tags : list of str, optional
            The tags associated with the given instance of this dataset.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.

        Returns
        -------
        str
            The appropariate filepath.
        """
        if self.singleton:
            return dataset_filepath(
                filename=self.fname(tags=tags, ext=ext),
                task=self.task,
                **self.kwargs,
            )
        return dataset_filepath(
            filename=self.fname(tags=tags, ext=ext),
            dataset_name=self.name,
            task=self.task,
            **self.kwargs,
        )

    def add_local(self, source_fpath, tags=None, ext=None):
        """Copies a given file into local store as an instance of this dataset.

        Parameters
        ----------
        source_fpath : str
            The full path for the source file to use.
        tags : list of str, optional
            The tags associated with the given instance of this dataset.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.
        """
        fpath = self.fpath(tags=tags, ext=ext)
        shutil.copyfile(src=source_fpath, dst=fpath)

    def upload(self, tags=None, ext=None, source_fpath=None, **kwargs):
        """Uploads the given instance of this dataset to dataset store.

        Parameters
        ----------
        tags : list of str, optional
            The tags associated with the given instance of this dataset.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.
        source_fpath : str, optional
            The full path for the source file to use. If given, the file is
            copied from the given path to the local storage path before
            uploading.
        **kwargs : extra keyword arguments
            Extra keyword arguments are forwarded to
            azure.storage.blob.BlockBlobService.create_blob_from_path.
        """
        if source_fpath:
            self.add_local(source_fpath=source_fpath, tags=tags, ext=ext)
        fpath = self.fpath(tags=tags, ext=ext)
        upload_dataset(
            dataset_name=self.name,
            file_path=fpath,
            task=self.task,
            dataset_attributes=self.kwargs,
            **kwargs,
        )

    def download(self, tags=None, ext=None, **kwargs):
        """Downloads the given instance of this dataset from dataset store.

        Parameters
        ----------
        tags : list of str, optional
            The tags associated with the given instance of this dataset.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.
        **kwargs : extra keyword arguments
            Extra keyword arguments are forwarded to
            azure.storage.blob.BlockBlobService.get_blob_to_path.
        """
        fpath = self.fpath(tags=tags, ext=ext)
        download_dataset(
            dataset_name=self.name,
            file_path=fpath,
            task=self.task,
            dataset_attributes=self.kwargs,
            **kwargs,
        )

    def _fname_patten(self, tags=None):
        return '{}{}{}'.format(
            self.fname_base,
            self._tags_to_str(tags),
            self.EXT_PATTERN,
        )

    def _find_extension(self, tags=None):
        fpattern = self._fname_patten(tags=tags)
        if self.singleton:
            data_dir = dataset_dirpath(task=self.task, **self.kwargs)
        else:
            data_dir = dataset_dirpath(
                dataset_name=self.name, task=self.task, **self.kwargs)
        for fname in os.listdir(data_dir):
            match = re.match(fpattern, fname)
            if match:
                return match.group(1)
        return None

    def df(self, tags=None, ext=None, **kwargs):
        """Loads an instance of this dataset into a dataframe.

        Parameters
        ----------
        tags : list of str, optional
            The tags associated with the desired instance of this dataset.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.
        **kwargs : extra keyword arguments, optional
            Extra keyword arguments are forwarded to the deserialization method
            of the SerializationFormat object corresponding to the extension
            used.

        Returns
        -------
        pandas.DataFrame
            A dataframe containing the desired instance of this dataset.
        """
        ext = self._find_extension(tags=tags)
        if ext is None:
            if tags is None:
                raise MissingDatasetError("No instance of {} dataset!".format(
                    self.name))
            raise MissingDatasetError(
                "No instance of dataset {} with tags: {}".format(
                    self.name, tags))
        fpath = self.fpath(tags=tags, ext=ext)
        fmt = SerializationFormat.by_name(ext)
        return fmt.deserialize(fpath, **kwargs)

    def dump_df(self, df, tags=None, ext=None, **kwargs):
        """Dumps an instance of this dataset into a file.

        Parameters
        ----------
        df : pandas.DataFrame
            The dataframe to dump to file.
        tags : list of str, optional
            The tags associated with the given instance of this dataset.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.
        **kwargs : extra keyword arguments, optional
            Extra keyword arguments are forwarded to the serialization method
            of the SerializationFormat object corresponding to the extension
            used.
        """
        if ext is None:
            ext = self.default_ext
        fpath = self.fpath(tags=tags, ext=ext)
        fmt = SerializationFormat.by_name(ext)
        fmt.serialize(df, fpath, **kwargs)

    def upload_df(self, df, tags=None, ext=None, **kwargs):
        """Dumps an instance of this dataset into a file and then uploads it
        to dataset store.

        Parameters
        ----------
        df : pandas.DataFrame
            The dataframe to dump and upload.
        tags : list of str, optional
            The tags associated with the given instance of this dataset.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.
        **kwargs : extra keyword arguments, optional
            Extra keyword arguments are forwarded to the serialization method
            of the SerializationFormat object corresponding to the extension
            used.
        """
        self.dump_df(df=df, tags=tags, ext=ext, **kwargs)
        self.upload(tags=tags, ext=ext)
