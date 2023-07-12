import fnmatch
import os
import tarfile
import time

from pathlib import Path
from scripts.ilapfuncs import *
from zipfile import ZipFile

from fnmatch import _compile_pattern
from functools import lru_cache
normcase = lru_cache(maxsize=None)(os.path.normcase)

class FileSeekerBase:
    # This is an abstract base class
    def search(self, filepattern_to_search, return_on_first_hit=False):
        '''Returns a list of paths for files/folders that matched'''
        pass

    def cleanup(self):
        '''close any open handles'''
        pass

class FileSeekerDir(FileSeekerBase):
    def __init__(self, directory):
        FileSeekerBase.__init__(self)
        self.directory = directory
        self._all_files = []
        logfunc('Building files listing...')
        self.build_files_list(directory)
        logfunc(f'File listing complete - {len(self._all_files)} files')

    def build_files_list(self, directory):
        '''Populates all paths in directory into _all_files'''
        try:
            files_list = os.scandir(directory)
            for item in files_list:
                self._all_files.append(item.path)
                if item.is_dir(follow_symlinks=False):
                    self.build_files_list(item.path)
        except Exception as ex:
            logfunc(f'Error reading {directory} ' + str(ex))

    def search(self, filepattern, return_on_first_hit=False):
        pat = _compile_pattern( normcase(filepattern) )
        root = normcase("root/")
        if return_on_first_hit:
            for item in self._all_files:
                if pat( root + normcase(item) ) is not None:
                    return [item]
            return []
        pathlist = []
        for item in self._all_files:
            if pat( root + normcase(item) ) is not None:
                pathlist.append(item)
        return pathlist

class FileSeekerTar(FileSeekerBase):
    def __init__(self, tar_file_path, temp_folder):
        FileSeekerBase.__init__(self)
        self.is_gzip = tar_file_path.lower().endswith('gz')
        mode ='r:gz' if self.is_gzip else 'r'
        self.tar_file = tarfile.open(tar_file_path, mode)
        self.temp_folder = temp_folder
        self.directory = temp_folder

    def search(self, filepattern, return_on_first_hit=False):
        pathlist = []
        pat = _compile_pattern( normcase(filepattern) )
        root = normcase("root/")
        for member in self.tar_file.getmembers():
            if pat( root + normcase(member.name) ) is not None:
                try:
                    clean_name = sanitize_file_path(member.name)
                    full_path = os.path.join(self.temp_folder, Path(clean_name))
                    if member.isdir():
                        os.makedirs(full_path, exist_ok=True)
                    else:
                        parent_dir = os.path.dirname(full_path)
                        if not os.path.exists(parent_dir):
                            os.makedirs(parent_dir)
                        with open(full_path, "wb") as fout:
                            fout.write(tarfile.ExFileObject(self.tar_file, member).read())
                            fout.close()
                        os.utime(full_path, (member.mtime, member.mtime))
                    pathlist.append(full_path)
                except Exception as ex:
                    logfunc(f'Could not write file to filesystem, path was {member.name} ' + str(ex))
        return pathlist

    def cleanup(self):
        self.tar_file.close()

class FileSeekerZip(FileSeekerBase):
    def __init__(self, zip_file_path, temp_folder):
        FileSeekerBase.__init__(self)
        self.zip_file = ZipFile(zip_file_path)
        self.name_list = self.zip_file.namelist()
        self.temp_folder = temp_folder
        self.directory = temp_folder

    def search(self, filepattern, return_on_first_hit=False):
        pathlist = []
        pat = _compile_pattern( normcase(filepattern) )
        root = normcase("root/")
        for member in self.name_list:
            if pat( root + normcase(member) ) is not None:
                try:
                    extracted_path = self.zip_file.extract(member, path=self.temp_folder) # already replaces illegal chars with _ when exporting
                    f = self.zip_file.getinfo(member)
                    date_time = f.date_time
                    date_time = time.mktime(date_time + (0, 0, -1))
                    os.utime(extracted_path, (date_time, date_time))
                    pathlist.append(extracted_path)
                except Exception as ex:
                    member = member.lstrip("/")
                    logfunc(f'Could not write file to filesystem, path was {member} ' + str(ex))
        return pathlist

    def cleanup(self):
        self.zip_file.close()
        