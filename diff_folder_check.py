import math as mp
import inspect
import os
import json
import sys
import numpy
import numpy.linalg
import time
from distutils.file_util import copy_file

def checksum_file_hexdigest(fn):
    chunksize = 1024*1024
    sha = hashlib.sha256()
    with open(fn,'rb') as f:
        data = f.read(chunksize)
        sha.update(data)
    return sha.hexdigest()

def get_one_way_diff_list(a,b):
    l = []
    for i in a:
        if i not in b:
            #print(i,' not in b')
            l.append(i)
    return l

def get_files_directory(startpath,remove_prefix=''):
    #walk file directory making a relative path list of each file
    if not os.path.isdir(startpath):
        return False

    listOfFiles = []
    dirpaths = []
    rolling_count = 0
    for (dirpath, dirnames, filenames) in os.walk(startpath):
        if not dirpath in dirnames:
            dirpaths.append(dirpath.removeprefix(remove_prefix))
        for file in filenames:
            relativepath = str(os.path.join(dirpath, file))
            listOfFiles +=  [relativepath.removeprefix(remove_prefix)]
    return [listOfFiles,dirpaths]

def makeChecksumFiles(startpath,folder_prefix='',file_prefix=''):
    files,dirs = get_files_directory(startpath)
    sorted(files)
    sorted(dirs)
    hashes = []
    with open(prefix + '\\' + file_prefix + '.files_hashes.' + os.path.relpath(startpath,prefix)) as f:
        for i in files:
            h = checksum_file_hexdigest(i)
            hashes.append(h)
            f.write(i + '|' + str(i))
    with open(prefix + '\\' + file_prefix + '.directory_structure.' + os.path.relpath(startpath,prefix)) as f:
            f.write(str(json.dump([files,dirs])))
    return [files,hashes,dirs]

#def getChecksumDifference(

def sync_missing_files_source_to_dest(fs,ds,source_prefix='',target_prefix='',makeHistoryHashMismatchedFiles=False,overwriteHashMismatcheFiles=False):
    for i in ds:
        try:
            os.makedirs(os.path.dirname(target_prefix + '\\' + i))
        except FileExistsError:
            pass
        except FileNotFoundError:
            pass

    for i in fs:
        print('copying-----',i)
        try:
            os.makedirs(os.path.dirname(target_prefix + '\\' + i))
        except FileExistsError:
            pass
        except FileNotFoundError:
            pass
        copy_file((source_prefix + '\\' + i), os.path.dirname(target_prefix + '\\' + i), True,True, False, verbose=True,dry_run=False)

#--------------------------------------------
        #
        #
        #       makeInitialChecksumFiles
        #       History on Hash Mismatch
        #       verbose
        #       overwrite Hash mismatches or make copy(history files) or 
        #       
        #       makeChecksumsAtEnd
        #
        #
        #
        
def sync(sourceAbsPath,sourcePrefix,targetAbsPath,targetPrefix,makeChecksumFiles=False,makeHistoryHashMismatchedFiles=False,overwriteHashMismatcheFiles=False,verbose=True):
    source_files,source_directories = get_files_directory(sourceAbsPath,sourcePrefix)
    target_files,target_directories = get_files_directory(targetAbsPath,targetPrefix)

    st_files = get_one_way_diff_list(source_files,target_files)
    ts_files = get_one_way_diff_list(target_files,source_files)
    st_dirs = get_one_way_diff_list(source_directories,target_directories)
    ts_dirs = get_one_way_diff_list(target_directories,source_directories)

    source_sorted_files, source_hashes = [],[]
    target_sorted_files, target_hashes = [],[]
    if makeChecksumFiles:
        source_sorted_files,source_hashes,source_dirs = makeChecksumFiles(sourceAbsPath,sourcePrefix)
        target_sorted_files,target_hashes,target_dirs = makeChecksumFiles(targetAbsPath,targetPrefix)

    if makeHistoryHashMismatchedFiles:
        pass
    
    if verbose:
        print('files missing from target folder---',st_files)
        print('files missing from source folder---',ts_files )
        print('directories missing from target folder---',st_dirs)
        print('directories missing from target folder---',ts_dirs)
    
    sync_missing_files_source_to_dest(st_files,st_dirs,sourcePrefix,targetPrefix)
    sync_missing_files_source_to_dest(ts_files,ts_dirs,targetPrefix,sourcePrefix)

sync('D:\\pv','D:\\','G:\\pv','G:\\')
sync('G:\\pv','G:\\','J:\\pv','J:\\')

