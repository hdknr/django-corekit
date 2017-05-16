# encoding: utf-8
from django.core.files.storage import FileSystemStorage as DjFileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class FileSystemStorage(DjFileSystemStorage):

    def __init__(self, *args, **kwargs):
        self.overwrite = kwargs.pop('overwrite', True)
        super(FileSystemStorage, self).__init__(*args, **kwargs)

    def get_available_name(self, name, max_length=None):
        if self.overwrite and self.exists(name):
            self.delete(name)

        return super(FileSystemStorage, self).get_available_name(
            name, max_length=max_length)
