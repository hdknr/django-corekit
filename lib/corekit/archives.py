# coding: utf-8
from django.core import serializers
import zipfile
from io import StringIO


class Zipball(object):
    def __init__(self):
        # Create the in-memory file-like object
        self.in_memory_zip = StringIO()

    def append(self, filename_in_zip, file_contents):
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(
            self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)

        # Write the file to the in-memory zip
        zf.writestr(filename_in_zip, file_contents)

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0

        return self

    def read(self):
        '''Returns a string with the contents of the in-memory zip.'''
        self.in_memory_zip.seek(0)
        return self.in_memory_zip.read()

    def writeto(self, stream):
        stream.write(self.read())

    def writetofile(self, filename):
        '''Writes the in-memory zip to a file.'''
        f = open(filename, "w")
        f.write(self.read())
        f.close()


class ModelZipball(Zipball):

    def append_query(self, queryset):
        file_name = "{}.{}.json".format(
            queryset.model._meta.app_label,
            queryset.model._meta.model_name)
        return self.append(
            file_name,
            serializers.serialize('json', queryset))
