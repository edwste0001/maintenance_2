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
    with open(folder_prefix + '\\' + os.path.relpath(startpath,folder_prefix) + file_appendix + '.files_hashes.txt','w') as f:
        for i in files:
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
            pathname.append(s1)
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

def folder_diff(sourceAbsPath,sourcePrefix,targetAbsPath,targetPrefix):
    pass
#---main sync stuff--------------------------------------------------
current_time = 0

key = "test key"

memory_input = []
memory_value = []

derangement_list = []
derangement_size = 0

#-----------------------------functions------------------------------
def memoize(f):

    def inner(n):
        i=0
        try:
            i = memory_input.index(n)
        except ValueError:
            #print('adding value')
            v = f(n)
            memory_input.append(n)
            memory_value.append(v)
            return v
        #print('recalling from memory')
        return memory_value[i]
        
    return inner

#---------------------------functions------------------------------
alphalist=[chr(i) for i in range(256)]

def array_index(arr, indices):
    if len(indices)==0:
        return arr
    return multiget_rec(arr[indices[0]], indices[1:])

def bitInvert(a):
    return ['1' if i=='0' else '0' for i in bin(int(a.hex(),base=16))[2:]]

def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='little')

def diff(fileList, folder1, folder2):
    for f in fileList:
        with open(str(folder1) + '\\' + f, 'rb') as file1, open(str(folder2) + '\\' + f, 'rb') as file2:
            data1 = file1.read()
            data2 = file2.read()

        if data1 != data2:
            print(f," Files do not match.")
        else:
            print(f," Files match.")

def getbinval(v):
    val = alphalist.index(v)
    v = bin(val)[2:]
    b = '0'*(8-len(v)) + v
    return b

def gettextval(v):
    return alphalist[int("0b"+"".join(v),2)]

def intToPaddedBitString(i):
    b = bin(i)[2:]
    return str('0'*(8-len(b)) + b)

def linear(a,y):
    #a*x mod 2**16 accepts 2 16 bit strings w/ front clipped off
    a = xor(a,'1010101010101010')
    #print(a,y)
    ai = int(a,2)
    yi = int(y,2)
    return (ai*yi) % (2**16)

def recursive_flatten(arr):
    l = []
    for i in range(len(arr)):
        isFlat = False
        try:
            if len(arr[i]) != 0:
                l = l + recursive_flatten(arr[i])
        except TypeError:
            isFlat = True
        if isFlat:
            l.append(arr[i])
    return l

def xor(i,j):
    s = ''
    for a,b in zip(i,j):
        if a=='1' and b=='1':
            s = s + '0'
        if a=='1' and b=='0':
            s = s + '1'
        if a=='0' and b=='1':
            s = s + '1'
        if a=='0' and b=='0':
            s = s + '0'
    return s

#-----------------------------derangement functions------------------------------
def applyDerangement(d,bits):
    #apply 8 bit derangement
    derangement = derangement_list[d]
    output_bits = [int(bits[i]) for i in range(len(bits))]
    m = numpy.identity(len(bits))
    
    for i,j in enumerate(derangement):
        m[i][i] = 0
        m[i][j] = 1

    return numpy.matmul(m,output_bits)

def applyReverseDerangement(d,bits):
    #apply 8 bit derangement
    derangement = derangement_list[d]
    output_bits = [int(bits[i]) for i in range(len(bits))]
    m = numpy.identity(len(bits))
   
    for i,j in enumerate(derangement):
        m[i][i] = 0
        m[i][j] = 1

    m = numpy.linalg.inv(m)
    
    return numpy.matmul(m,output_bits)

def get_derangements(n):
    numbers = [i for i in range(n)]
    print('----------',numbers,'------------')
    print(numbers)
    
    import itertools
    z = [i for i in itertools.permutations(numbers)]
    d = []
    count_by = [ [ 0 for i in range(n)] for j in range(n)  ]
    sums = [ 0 for i in range(n)]
    for i in z:
        f = True
        for j in range(n):
            if i[j]==j:
                f = False
        if f:
            d.append(list(i))
            for j in range(n):
                index = i[j]
                count_by[j][index] = count_by[j][index] + 1
                sums[j] = sums[j] + index
        #print(i)
    return d

@memoize 
def get_derangement_count(n):
    if n<0:
        raise
    if n==0:
        return 1
    if n==1:
        return 0
    return (n-1)*(get_derangement_count(n-1)+get_derangement_count(n-2))

#-----------------------------text encrypt/decrypt------------------------------
def text_decrypt(text,key):
    t = len(text)
    k = len(key)

    data = text

    i = 0
    offset = 0
    offset1 = 0
    ciphbytes = []
    for d in data:
        kbit0 = "".join(['0'*(8-len(getbinval(key[i]))) + getbinval(key[i])])
        i = (i + 1) % k
        kbit1 = "".join(['0'*(8-len(getbinval(key[i]))) + getbinval(key[i])])
        i = (i + 1) % k

        offset = bin(offset)[2:]
        offset = linear(kbit0+kbit1,offset)
        if offset > derangement_size:
            offset1 = offset - derangement_size
            ciphbytes.append(applyReverseDerangement(offset,intToPaddedBitString(d)))
            ciphbytes[-1] = applyReverseDerangement(offset1,ciphbytes[-1])
        else:
            ciphbytes.append(applyReverseDerangement(offset,intToPaddedBitString(d)))

    ciphbits = "".join(((str(int(i))) for i in recursive_flatten(ciphbytes)))

    b = bytes()

    for i in range(len(ciphbits)//8):
        b = b + bytes([int(ciphbits[8*i:8*(i+1)],2)])

    return b

def text_encrypt(text,key):
    t = len(text)
    k = len(key)
    if t < 6:
        raise
    if k < 4:
        raise

    data = str(len(text)) + ',' + text

    i = 0
    offset = 0
    offset1 = 0
    ciphbytes = []
    for d in data:
        kbit0 = "".join(['0'*(8-len(getbinval(key[i]))) + getbinval(key[i])])
        i = (i + 1) % k
        kbit1 = "".join(['0'*(8-len(getbinval(key[i]))) + getbinval(key[i])])
        i = (i + 1) % k
        dd = getbinval(d)

        offset = bin(offset)[2:]
        offset = linear(kbit0+kbit1,offset)
        if offset > derangement_size:
            offset1 = offset - derangement_size
            ciphbytes.append(applyDerangement(offset,dd))
            ciphbytes[-1] = applyDerangement(offset1,ciphbytes[-1])
        else:
            ciphbytes.append(applyDerangement(offset,dd))

    ciphbits = "".join(((str(int(i))) for i in recursive_flatten(ciphbytes)))

    b = bytes()

    for i in range(len(ciphbits)//8):
        b = b + bytes([int(ciphbits[8*i:8*(i+1)],2)])

    return b


#-----------------------------file/header functions------------------------------
def get_next_parsed_entry(z):
    z = z.lstrip()
    firstBracket = z.find('[')
    if z[0] == '|':
        return -1,z[firstBracket+1:]
    if firstBracket==-1:
        return [-1,-1]
    idx = firstBracket + 1
    #get string
    state = 0
    firstparenth, startint, secondstartint, file, count1, count2 = 0,0,0,'',0,0
    z = z.replace('\\\\','\\')
    while(state <= 4):
        #file string
        if(state == 0):
            if(z[idx]=='\''):
                firstparenth = idx
                state = state + 1
        elif(state == 1):
            if(z[idx]=='\''):
                file = z[firstparenth+1:idx]
                state = state + 1
        elif (state == 2):
            if(z[idx]==','):
                startint = idx
                state = state + 1
        elif (state == 3):
            if(z[idx]==','):
                #print('z------------',z)
                #print(z[startint+1:idx])
                count1 = int(z[startint+1:idx])
                secondstartint = idx
                state = state + 1
        elif (state == 4):
            if(z[idx]==']'):
                #print(z[startint+1:idx])
                count2 = int(z[secondstartint+1:idx])
                state = state + 1
        idx = idx + 1

    return [file,count1,count2], z[idx+1:]

def get_next_directory_entry(z):
    firstQuote = z.find('\'')
    if firstQuote==-1:
        return [-1,-1]
    
    idx = firstQuote + 1
    z = z[idx:]
    secondQuote = z.find('\'')
    
    if secondQuote == -1:
        return [-1,-1]
    s = z[0:secondQuote]
    s = s.replace('\\\\','\\')
    return s, z[secondQuote+1+len(', '):]
    
def get_header_file_sizes(storage_file_name,key):
    with open(storage_file_name,'rb') as storage_file:
        k = len(key)
        data = storage_file.read(1000)
        i = 0
        offset = 0
        offset1 = 0
        ciphbytes = []
        ciphbitstring = ''
        decoded_byte_string = b''
        #print('data',data)
        for d in data:
            kbit0 = "".join(['0'*(8-len(getbinval(key[i]))) + getbinval(key[i])])
            i = (i + 1) % k
            kbit1 = "".join(['0'*(8-len(getbinval(key[i]))) + getbinval(key[i])])
            i = (i + 1) % k

            offset = bin(offset)[2:]
            offset = linear(kbit0+kbit1,offset)
            if offset > derangement_size:
                offset1 = offset - derangement_size
                ciphbyte = applyReverseDerangement(offset,intToPaddedBitString(d))
                ciphbyte = applyReverseDerangement(offset1,ciphbyte)
            else:
                ciphbyte = applyReverseDerangement(offset,intToPaddedBitString(d))

            ciphbitstring = "".join((str(int(i)) for i in ciphbyte))
            print(decoded_byte_string)
            cbs = bytes([int(ciphbitstring,2)])
            

            if cbs==b',':
                print('break')
                break

            decoded_byte_string = decoded_byte_string + cbs

        return int(decoded_byte_string)

def get_files_directory(startpath):
    #walk file directory making a relative path list of each file
    if not os.path.isdir(startpath):
        return False

    listOfFiles = []
    dirpaths = []
    rolling_count = 0
    for (dirpath, dirnames, filenames) in os.walk(startpath):
        if not dirpath in dirnames:
            dirpaths.append(dirpath)
        for file in filenames:
            sz = os.path.getsize(os.path.join(dirpath, file))

            #startpathlength = len(str(os.path.join(startpath)))
            relativepath = str(os.path.join(dirpath, file))

            listOfFiles += [ [relativepath, rolling_count, sz] ]
            rolling_count += sz
    return listOfFiles,dirpaths

def decrypt_file_list(storage_file_name,key):
    header_length = get_header_file_sizes(storage_file_name,key)
    with open(storage_file_name,'rb') as storage_file:
        storage_file.seek(len(str(header_length))+1)
        crypt_header = storage_file.read(header_length)
        print('----------list_folder_files------------')
        print('---crypt_header----------------')
        print(crypt_header)
        
        listOfFiles,dirList = decrypt_header(crypt_header,key)
        print('------listOfFiles--------------')
        print(listOfFiles)
        print('------dirOfFiles---------------')
        print(dirList)
    return listOfFiles,dirList
    
def decrypt_header(s,key):
    #fails on bunch of empty folders and nothing else
    #ie empty file list
    #print('header pre decrypt header',s)
    header = text_decrypt(s,key).decode('utf-8')
    #print('header post decrypt header',header)
    header = header.rstrip('_')
    firstBracket = header.find('[')
    lastBracket = header.rfind(']')
    if firstBracket!=0 and lastBracket!= len(header):
        return []
    header = header[1:-1]
    z = get_next_parsed_entry(header)
    entry,header = z
    l = []
    while entry != -1:
        l.append(entry)
        #print('l',l)
        entry,header = get_next_parsed_entry(header)
        #print('entry----------',entry)
        #print('header---------',header)
    nextBracket = header.find('[')
    header = header[nextBracket+1:]
    d = []
    entry,header = get_next_directory_entry(header)
    while entry != -1:
        d.append(entry)
        entry,header = get_next_directory_entry(header)
        
    return l,d

def decrypt_file_from_storage(start_pos, filename, filesize, encrypted_locker_filename, key):
    #decrypt_file
    #check that this works
    sz = filesize
    k = len(key)

    data = None
    chunksize = 1024*1024
    
    try:
        os.makedirs(os.path.dirname(filename))
    except FileExistsError:
        pass
    except FileNotFoundError:
        pass
    
    with open(encrypted_locker_filename,mode='rb') as f:
        f.seek(start_pos)
        
        with open(filename,mode='wb') as fo:

            data = f.read(filesize)
            #print(data)

            i = 0
            offset = 0
            offset1 = 0
            
            for d in data:
                ciphbytes = []
                kbit0 = "".join(['0'*(8-len(getbinval(key[i]))) + getbinval(key[i])])
                i = (i + 1) % k
                kbit1 = "".join(['0'*(8-len(getbinval(key[i]))) + getbinval(key[i])])
                i = (i + 1) % k

                offset = bin(offset)[2:]
                offset = linear(kbit0+kbit1,offset)
                
                if offset > derangement_size:
                    offset1 = offset - derangement_size
                    ciphbytes.append(applyDerangement(offset,intToPaddedBitString(d)))
                    ciphbytes[-1] = applyDerangement(offset1,ciphbytes[-1])
                else:
                    ciphbytes.append(applyDerangement(offset,intToPaddedBitString(d)))

                for z in ciphbytes:
                    fo.write(bytes([int(''.join([str(int(j)) for j in z]),2)]))

def get_tick():
    global current_time
    new_time = time.perf_counter()
    elapsed = new_time - current_time
    current_time = elapsed
    return elapsed

def encrypt_file_for_storage(filename, storage_file, key):
    k = len(key)
    byte_key = key.encode('utf-8')
    sz = os.path.getsize(filename)
    chunksize = 1024*1024
    bytesread = 0
    current_key = 0
    offset = 0
    
    with open(filename,mode='rb') as f:
        intsz = bin(sz)[2:]

        data = 'start'
        offset = 0
        offset1 = 0
        i = 0
        while not data==b'':
            data = f.read(chunksize)
            #print('len of data',len(data),end='')

            for ii,d in enumerate(data):
                ciphbytes = []
                if ii%10000 == 0:
                    print(ii,'\t',end='')
                kbit0 = intToPaddedBitString(byte_key[i])
                i = (i + 1) % k
                kbit1 = intToPaddedBitString(byte_key[i])
                i = (i + 1) % k

                offset = bin(offset)[2:]
                offset = linear(kbit0+kbit1,offset)
                
                if offset > derangement_size:
                    offset1 = offset - derangement_size
                    ciphbytes.append(applyDerangement(offset,intToPaddedBitString(d)))
                    ciphbytes[-1] = applyDerangement(offset1,ciphbytes[-1])
                else:
                    ciphbytes.append(applyDerangement(offset,intToPaddedBitString(d)))

                for z in ciphbytes:
                    storage_file.write(bytes([int(''.join([str(int(j)) for j in z]),2)]))            

def decrypt_folder(new_folder_name,storage_file_name,key):
    listofFiles,dir_list = decrypt_file_list(storage_file_name,key)
    start_offset = get_header_file_sizes(storage_file_name,key)
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<decrypt<<<<<<<<<<<<<<<<<<<<<<<')
    start_offset = start_offset + len(str(start_offset)) + 1
    print(start_offset)
    print('----------list_folder_files----------')
    print(listofFiles)
    print('----------dir_list-------------------')
    print(dir_list)
    for d in dir_list:
        print(d)
        try:
            os.makedirs(new_folder_name+'//'+d)
        except FileExistsError:
            pass
        except FileNotFoundError:
            pass

    for filetuple in listofFiles:
        #start_pos, filename, filesize, encrypted_locker_filename, key
        print('--------------------------------',new_folder_name+'//'+filetuple[0],start_offset+filetuple[1])
        decrypt_file_from_storage(start_offset+filetuple[1], new_folder_name+ '//'+filetuple[0], filetuple[2], storage_file_name, key)
    
def encrypt_folder(startpath,storage_file_name,key):
    print('----encrypt_folder_step------')
    file_list,dir_list = get_files_directory(startpath)
    full_header = str(file_list)+'|'+str(dir_list)
    header_length = len(full_header)
    print('---')
    print(file_list)
    print('---')
    print(dir_list)
    print('---')
    file_sizes_crypted = text_encrypt(full_header,key)
    
    print(file_list)
    print('---header--length----------')
    print(header_length)
    print('------------------------')
    
    with open(storage_file_name,'wb') as storage_file:
        #check for length mismatch
        storage_file.write(file_sizes_crypted)
        for current_file_header in file_list:
            print(os.path.basename(current_file_header[0]))
            encrypt_file_for_storage(current_file_header[0], storage_file, key)



derangement_list = get_derangements(8)
derangement_size = len(derangement_list)

folder = input('enter folder name')
binfile = input('bin file')
key = input('enter key')

encrypt_folder('test',binfile,key)

new_folder = input('enter new folder name')

decrypt_folder('test out',binfile,key)

get_one_way_diff_list(a,b)



