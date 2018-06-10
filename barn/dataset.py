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

    @staticmethod
    def _version_to_str(version=None):
        return '_{}'.format(version) if version else ''

    def fname(self, version=None, tags=None, ext=None):
        """Returns the filename appropriate for an instance of this dataset.

        Parameters
        ----------
        version: str, optional
            The version of the instance of this dataset.
        tags : list of str, optional
            The tags associated with the instance of this dataset.
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
        return '{}{}{}.{}'.format(
            self.fname_base,
            self._tags_to_str(tags=tags),
            self._version_to_str(version=version),
            ext,
        )

    def fpath(self, version=None, tags=None, ext=None):
        """Returns the filepath appropriate for an instance of this dataset.

        Parameters
        ----------
        version: str, optional
            The version of the instance of this dataset.
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
                filename=self.fname(version=version, tags=tags, ext=ext),
                task=self.task,
                **self.kwargs,
            )
        return dataset_filepath(
            filename=self.fname(version=version, tags=tags, ext=ext),
            dataset_name=self.name,
            task=self.task,
            **self.kwargs,
        )

    def add_local(self, source_fpath, version=None, tags=None):
        """Copies a given file into local store as an instance of this dataset.

        Parameters
        ----------
        source_fpath : str
            The full path for the source file to use.
        version: str, optional
            The version of the instance of this dataset.
        tags : list of str, optional
            The tags associated with the given instance of this dataset.

        Returns
        -------
        ext : str
            The extension of the file added.
        """
        ext = os.path.splitext(source_fpath)[1]
        ext = ext[1:]  # we dont need the dot
        fpath = self.fpath(version=version, tags=tags, ext=ext)
        shutil.copyfile(src=source_fpath, dst=fpath)
        return ext

    def _fname_pattern(self, version=None, tags=None):
        return '{}{}{}{}'.format(
            self.fname_base,
            self._tags_to_str(tags),
            self._version_to_str(version),
            self.EXT_PATTERN,
        )

    def _find_extension(self, version=None, tags=None):
        fpattern = self._fname_pattern(version=version, tags=tags)
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

    def upload(self, version=None, tags=None, ext=None, source_fpath=None,
               overwrite=False, **kwargs):
        """Uploads the given instance of this dataset to dataset store.

        Parameters
        ----------
        version: str, optional
            The version of the instance of this dataset.
        tags : list of str, optional
            The tags associated with the given instance of this dataset.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used. If source_fpath is given, this is ignored, and the extension
            of the source f
        source_fpath : str, optional
            The full path for the source file to use. If given, the file is
            copied from the given path to the local storage path before
            uploading.
        **kwargs : extra keyword arguments
            Extra keyword arguments are forwarded to
            azure.storage.blob.BlockBlobService.create_blob_from_path.
        """
        if source_fpath:
            ext = self.add_local(
                source_fpath=source_fpath, version=version, tags=tags)
        if ext is None:
            ext = self._find_extension(version=version, tags=tags)
        if ext is None:
            attribs = "{}{}".format(
                "version={} and ".format(version) if version else "",
                "tags={}".format(tags) if tags else "",
            )
            raise MissingDatasetError(
                "No dataset with {} in local store!".format(attribs))
        fpath = self.fpath(version=version, tags=tags, ext=ext)
        if not os.path.isfile(fpath):
            attribs = "{}{}ext={}".format(
                "version={} and ".format(version) if version else "",
                "tags={} and ".format(tags) if tags else "",
                ext,
            )
            raise MissingDatasetError(
                "No dataset with {} in local store! (path={})".format(
                    attribs, fpath))
        upload_dataset(
            dataset_name=self.name,
            file_path=fpath,
            task=self.task,
            dataset_attributes=self.kwargs,
            **kwargs,
        )

    def download(self, version=None, tags=None, ext=None, overwrite=False,
                 verbose=False, **kwargs):
        """Downloads the given instance of this dataset from dataset store.

        Parameters
        ----------
        version: str, optional
            The version of the instance of this dataset.
        tags : list of str, optional
            The tags associated with the given instance of this dataset.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.
        overwrite : bool, default False
            If set to True, the given instance of the dataset is downloaded
            from dataset store even if it exists in the local data directory.
            Otherwise, if a matching dataset is found localy, download is
            skipped.
        verbose : bool, default False
            If set to True, informative messages are printed.
        **kwargs : extra keyword arguments
            Extra keyword arguments are forwarded to
            azure.storage.blob.BlockBlobService.get_blob_to_path.
        """
        fpath = self.fpath(version=version, tags=tags, ext=ext)
        if os.path.isfile(fpath) and not overwrite:
            if verbose:
                print(
                    "File exists and overwrite set to False, so not "
                    "downloading {} with version={} and tags={}".format(
                        self.name, version, tags))
                return
        download_dataset(
            dataset_name=self.name,
            file_path=fpath,
            task=self.task,
            dataset_attributes=self.kwargs,
            **kwargs,
        )

    def df(self, version=None, tags=None, ext=None, **kwargs):
        """Loads an instance of this dataset into a dataframe.

        Parameters
        ----------
        version: str, optional
            The version of the instance of this dataset.
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
        ext = self._find_extension(version=version, tags=tags)
        if ext is None:
            attribs = "{}{}".format(
                "version={} and ".format(version) if version else "",
                "tags={}".format(tags) if tags else "",
            )
            raise MissingDatasetError(
                "No dataset with {} in local store!".format(attribs))
        fpath = self.fpath(version=version, tags=tags, ext=ext)
        fmt = SerializationFormat.by_name(ext)
        return fmt.deserialize(fpath, **kwargs)

    def dump_df(self, df, version=None, tags=None, ext=None, **kwargs):
        """Dumps an instance of this dataset into a file.

        Parameters
        ----------
        df : pandas.DataFrame
            The dataframe to dump to file.
        version: str, optional
            The version of the instance of this dataset.
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
        fpath = self.fpath(version=version, tags=tags, ext=ext)
        fmt = SerializationFormat.by_name(ext)
        fmt.serialize(df, fpath, **kwargs)

    def upload_df(self, df, version=None, tags=None, ext=None, **kwargs):
        """Dumps an instance of this dataset into a file and then uploads it
        to dataset store.

        Parameters
        ----------
        df : pandas.DataFrame
            The dataframe to dump and upload.
        version: str, optional
            The version of the instance of this dataset.
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
        self.dump_df(df=df, version=version, tags=tags, ext=ext, **kwargs)
        self.upload(version=version, tags=tags, ext=ext)
