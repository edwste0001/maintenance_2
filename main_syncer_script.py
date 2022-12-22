import math as mp
import inspect
import os
import json
import sys
import numpy
import numpy.linalg
import time
import hashlib
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
        print(startpath,remove_prefix,' is not a directory.')
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
    print (listOfFiles,dirpaths)
    return [listOfFiles,dirpaths]

def makeChecksumFiles(startpath,folder_prefix='',file_appendix=''):
    #can't have local folder path be 
    files,dirs = get_files_directory(startpath)
    sorted(files)
    sorted(dirs)
    hashes = []
    print(folder_prefix)
    print(os.path.relpath(startpath,folder_prefix))
    print(file_appendix)
    with open(folder_prefix + '\\' + os.path.relpath(startpath,folder_prefix) + file_appendix + '.files_hashes.txt','w') as f:
        for i in files:
            #probably a little buggy
            h = checksum_file_hexdigest(i)
            hashes.append(h)
            f.write(i + '|' + str(h) + '\n')
    with open(folder_prefix + '\\' + os.path.relpath(startpath,folder_prefix) + file_appendix + '.directory_structure.txt','w') as f:
            f.write(str(json.dumps([files,dirs])))
    return [files,hashes,dirs]

def dedupFolder(startpath,folder_prefix='',file_prefix=''):
    makeChecksumFiles(startpath,folder_prefix,file_prefix)
    

def sync_missing_files_source_to_dest(fs,ds,source_prefix='',target_prefix='',makeHistoryHashMismatchedFiles=False,overwriteHashMismatcheFiles=False):
    for i in ds:
        try:
            os.makedirs(os.path.dirname(target_prefix + '\\' + i))
        except FileExistsError:
            pass
        except FileNotFoundError:
            pass
        except PermissionError:
            print('Permission Error when making directory for:',target_prefix + '\\' + i)
            pass

    for i in fs:
        print('copying-----',i)
        try:
            os.makedirs(os.path.dirname(target_prefix + '\\' + i))
        except FileExistsError:
            pass
        except FileNotFoundError:
            pass
        except PermissionError:
            print('Permission Error when making directory for:',target_prefix + '\\' + i)
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

        
def sync(sourceAbsPath,sourcePrefix,targetAbsPath,targetPrefix,makeChecksumFiles=False,makeHistoryHashMismatchedFiles=False,overwriteHashMismatcheFiles=False,verbose=True):
    print('getting source dirs')
    source_files,source_directories = get_files_directory(sourceAbsPath,sourcePrefix)
    print('getting target dirs')
    target_files,target_directories = get_files_directory(targetAbsPath,targetPrefix)
    print('getting diff lists')
    st_files = get_one_way_diff_list(source_files,target_files)
    ts_files = get_one_way_diff_list(target_files,source_files)
    st_dirs = get_one_way_diff_list(source_directories,target_directories)
    ts_dirs = get_one_way_diff_list(target_directories,source_directories)

    source_sorted_files, source_hashes = [],[]
    target_sorted_files, target_hashes = [],[]
#    if makeChecksumFiles:
#        source_sorted_files,source_hashes,source_dirs = makeChecksumFiles(sourceAbsPath,sourcePrefix)
#        target_sorted_files,target_hashes,target_dirs = makeChecksumFiles(targetAbsPath,targetPrefix)

#    if makeHistoryHashMismatchedFiles:
#        pass
    
    if verbose:
        print('files missing from target folder---',st_files)
        print('files missing from source folder---',ts_files)
        print('directories missing from target folder---',st_dirs)
        print('directories missing from target folder---',ts_dirs)
    
    sync_missing_files_source_to_dest(st_files,st_dirs,sourcePrefix,targetPrefix)
    sync_missing_files_source_to_dest(ts_files,ts_dirs,targetPrefix,sourcePrefix)
    #start='F:\\data\\manual backups\\thumbdrives\\pv\\'

#l = ['C:\\','D:\\','F:\\','G:\\','H:\\','I:\\','J:\\']
#start='data\\code'
def loadFileHashes(startpath,folder_prefix='',file_appendix=''):
    #is not localized
    pathname = []
    hashes = []
    with open(folder_prefix + '\\' + os.path.relpath(startpath,folder_prefix) + file_appendix + '.files_hashes.txt','r') as f:
        data = '0'
        while data != '':
            s = f.readline()
            s = s.replace('\n','')
            if s=='':
                break
            s1, s2 = s.split('|')
            z = os.path.relpath(s1,folder_prefix)
            pathname.append(z)
            hashes.append(s2)
    return [pathname,hashes]
    
def getdeduplicationlist(startpath,folder_prefix='',file_appendix='',loadHashesFromFile=False,getfilestoremoveonly=True,removeFiles=False):
    print('deduplicating')
    print('------loading hash file------------')
    if loadHashesFromFile:
        pathname,hashes = loadFileHashes(startpath,folder_prefix,file_appendix)
    else:
        makeChecksumFiles(startpath,folder_prefix,file_appendix)
        pathname,hashes = loadFileHashes(startpath,folder_prefix,file_appendix)
    fileCrossReferenceIndexList = []
    logFile = None
    if removeFiles:
        logFile = open('SyncerlogFile.txt','w')
            
    #add exclusion thingy if needed in the future...otherwise just run through them verbatim
    print('------looking for duplicates------')
    for i,file in enumerate(pathname):
        fileCrossReferenceIndexList.append([i])
        for j,second_file in enumerate(pathname):
            if i==j:
                continue
            if hashes[i]==hashes[j]:
                fileCrossReferenceIndexList[-1].append(j)
    #fix this with translation back to file names
    #optional with prefix or without probably be nice
    equivalentFileList = []
    print('building duplicate list')
    for f in fileCrossReferenceIndexList:
        short_list = []
        for g in f:
            short_list.append(pathname[g])
        if not getfilestoremoveonly:
            equivalentFileList.append(short_list)
        else:
            equivalentFileList.append(short_list[1:])
            #turn this off for now
            '''
            if False:
                print('----removing files------')
                for s in short_list[1:]:
                    
                    print('---removing---',s)
                    logFile.write(str('---removing---'+s))
                    try:
                        os.remove(s)
                    except FileNotFoundError:
                        print("File not found",s)
                        logFile.write(str("File not found:"+s))
                    except PermissionError:
                        print("Permission Error",s)
                        logFile.write(str("File not found:"+s))
            '''

    
    return equivalentFileList

def checkDirectorySimilarityWithHashes(hashFileLeftPath,hashFileLeftFname,hashFileRightPath,hashFileRightFname,hashFileLeftPrefix='',hashFileRightPrefix='',fileAppendixLeft='',fileAppendixRight='',loadHashesFromFile=False):


    print('------making hash file------------')
    #if loadHashesFromFile:
    #    lpathname,lhashes = loadFileHashes(hashFileLeft,hashFileLeftPrefix,fileAppendixLeft)
    #    rpathname,rhashes = loadFileHashes(hashFileRight,hashFileRightPrefix,fileAppendixRight)
    #else:
        
    makeChecksumFiles(hashFileLeftPath,hashFileLeftPrefix)
    makeChecksumFiles(hashFileRightPath,hashFileRightPrefix)
    print('------loading hash file------------')
    lpathname,lhashes = loadFileHashes(hashFileLeftPath,hashFileLeftPrefix)
    rpathname,rhashes = loadFileHashes(hashFileRightPath,hashFileRightPrefix)
    #lpathname = [os.path.relpath(i,'F:\\data\\code\\old_code_chunk_1_2022') for i in lpathname]
    #rpathname = [os.path.relpath(i,'F:\\data\\code\\old_code_chunk_1_2022_dold_code_chunk_1_2022') for i in rpathname]
    
    l_diff_list = get_one_way_diff_list(lpathname,rpathname)
    r_diff_list = get_one_way_diff_list(rpathname,lpathname)
    print('-------length of hash file--------')
    print(l_diff_list)
    print(r_diff_list)
    if(len(l_diff_list)!=0 or len(r_diff_list)!=0):
        print('diff_lists are not the same...folders are different')
        raise
    #add exclusion thingy if needed in the future...otherwise just run through them verbatim
    print('------looking for hash mismatches------')
    for i,file in enumerate(lpathname):
        for j,second_file in enumerate(rpathname):
            if i==j and lhashes[i]!=rhashes[j]:
                print('-----------hash mismatch in files',file,second_file,lhashes[i],rhashes[j],'-----------------')
                raise
    print('directories match up')


checkDirectorySimilarityWithHashes('F:\\data\\code','F:\\data\\code\\code_d',\
                                   'F:\\data\\code','F:\\data\\code\\code_test_argcode_d',\
                                   'F:\\data\\code','F:\\data\\code')

















