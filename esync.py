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

sys.setrecursionlimit(1500)

current_time = 0



key = "test key"
#------listify code-------
def xor(a,b):
    if a and b:
        return True
    if not a and not b:
        return True
    return False

class testclass():
    def testmethod(self):
        pass

testclassobject = testclass()

def test():
    pass

#code is not perfect...has errors
simple_type_list = [ 5, True, 'test_string']
method_list =  [ test, hex, testclassobject.testmethod ]
other_method_lists = [ '<class \'method\'>', '<bound method','method','frame','code']

def listify(ob):
    final_list = []
    #get list of vars

    l = list(filter(lambda x:xor(x.find('__')==-1,x.find('__main__')==-1),dir(ob)))
    #print('')
    #print('')
    #print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>dir list',dir(ob))
    #print('')
    #print('')
    #print('-------------------------------------filtered dir list',l)
    f = False
    for item in l:
        #if is not a simple type
        #if item in attribute_black_list:
        #    continue
        #print([str((type(getattr(ob,item)))) == str(type(t)) for t in simple_type_list])
        #if item=='dirEntryItems':
            #f = True
            #print('type----------',str((type(getattr(ob,item)))))
            #print([str(type(getattr(ob,item))) == str(type(t)) for t in simple_type_list])
            #print(not any([str(type(getattr(ob,item))) == str(type(t)) for t in simple_type_list]))
        if not any([str(type(getattr(ob,item))) == str(type(t)) for t in simple_type_list]):
            if (str(type(getattr(ob,item))) == str(type(list([])))):
                if f:
                    print('list found')
                print('list type----------',item,'--------------------------',len(getattr(ob,item)),'------------------------------------')
                list_reference = getattr(ob,item)
                ll = [  [   list_reference[i],   listify(list_reference[i])    ]   for i in range(len(list_reference))]
                final_list.append([item,str(type(list_reference)),ll])
            else:
                if any(str((type(getattr(ob,item)))) == str(type(t)) for t in method_list):
                    if f:
                        print('method found')
                else:
                    if f:
                        print([str((type(getattr(ob,item)))).find(str(t))!=-1  for t in other_method_lists])
                    if any(str((type(getattr(ob,item)))).find(str(t))!=-1  for t in other_method_lists):
                        if f:
                            print('method found')
                    else:
                        if f:
                            print('non simple object found')
                        final_list.append([item,str(type(getattr(ob,item))),listify(getattr(ob,item))])
        else:
            if f:
                print('simple type found')
            final_list.append([item,str(type(getattr(ob,item))),getattr(ob,item)])
        f=False
    return final_list
#----------end-listify-code-------

def isIn(l,var,n):
    for i in l:
        if getattr(i,var) == n:
            return True
    return False

def getIndexByIsIn(l,var,n):
    for i,item in enumerate(l):
        if getattr(i,var) == n:
            return i
    return -1

def getObjectByIsIn(l,var,n):
    for i in l:
        if getattr(i,var) == n:
            return i
    return -1

def parsePath(p):
    if p[-1] == '\\':
        print('folder paths cant be ended in slashes')
        if 1==1:
            raise
        p = p[:-1]
    i = p.rfind('\\')
    if i == -1:
        return '',path
    else:
        return path[0:i],path[i+1:]

class fileObject:
    def __init__(self):
        pass
    def __init__(self,path,name,genChecksum=True):
        self.path,self.name = path,name

        if genChecksum:
            self.getHash()
            
    def is_dir(self):
        return False
    #other attributes include
    #relativepath
        
    #---------helper funcs-----
    def checksum_file_hexdigest(fn):
        chunksize = 1024*1024
        sha = hashlib.sha256()
        with open(fn,'rb') as f:
            data = f.read(chunksize)
            sha.update(data)
        return sha.hexdigest()
    #--------------------------
    def getHash(self):
        print('generating hash for',self.path)
        self.hash = fileObject.checksum_file_hexdigest(self.path)
        
class fileHashingObject:
    def __init__(self):
        pass
    def __init__(self,fn):
        pass
       
class syncObject:
    def __init__(self):
        self.populate_source=True
        self.populate_target=True


class folderObject:
    def __init__(self):
        pass
        
    def __init__(self,path,name,auto_populate=True,genChecksum=True):
        self.path = path
        self.name = name
        self.items = []
        self.names = []
        
        if auto_populate:
            self.autoPopulate(genChecksum)

    def is_dir(self):
        return True

    def autoPopulate(self,genChecksum=True):
        self.items = []
        self.names = []
        #self.itemDirEntryIndexCrossReference = []
        print('folder path----',self.path)
        self.dirEntryItems = [i for i in os.scandir(self.path)]
        print([[i,i.is_file(),i.is_dir()] for i in self.dirEntryItems])
        for i,s in enumerate(self.dirEntryItems):
            #print('s.is_dir()',s.is_dir())
            if s.is_dir():
                print('Folder Found',s)
                print('s.path','s.name',s.path,s.name)
                f = folderObject(s.path,s.name,genChecksum)
                self.items.append(f)
                #self.itemDirEntryIndexCrossReference.append(i)
                self.names.append(s.name)
            else:
                f = fileObject(s.path,s.name,genChecksum)
                self.items.append(f)
                #self.itemDirEntryIndexCrossReference.append(i)
                self.names.append(s.name)
            
#make data serializer
class SyncFolderInfoObject:
    #target folder
    #source folder
    #hashes for all files
    def __init__(self):
        pass
    def __init__(self,sourcePath,targetPath,autoPopulate=True,syncScanFolders=True,autoSync=True,genHashes=False,loadHashes=False,saveHashes=False):
        self.s_add_list = []
        self.s_update_list = []
        self.s_synced_list = []
        
        self.t_add_list = []
        self.t_update_list = []
        self.t_synced_list = []
        
        self.sourcePath = sourcePath
        self.targetPath = targetPath
        
        self.syncChildrenFolders = []

        self.is_populated=False
        self.is_synced=False
        self.is_scanned=False
        self.is_source_synced=False
        self.is_target_synced=False

        self.autoPopulate = autoPopulate
        self.syncScanFolders = syncScanFolders
        self.autoSync = autoSync
        self.genHashes = genHashes
        self.loadHashes= loadHashes
        self.saveHashes= saveHashes

        self.sourceFolderExists=os.path.exists(sourcePath)
        self.targetFolderExists=os.path.exists(targetPath)

        if autoPopulate:
            print('populating',self.sourcePath)
            if self.sourceFolderExists:
                self.sourceFolder = folderObject(os.path.abspath(sourcePath),os.path.basename(sourcePath),autoPopulate,genHashes)
            if self.targetFolderExists:
                self.targetFolder = folderObject(os.path.abspath(targetPath),os.path.basename(targetPath),autoPopulate,genHashes)
            self.is_populated = True

        if syncScanFolders:
            if self.is_populated:
                self.genSyncFolders()
            else:
                print('populate file system first')
                raise
        if loadHashes:           
            self.loadHashesFromFiles()
            
        if saveHashes:
            self.saveHashesToFile()

        if autoSync:
            if self.is_scanned:
                self.sync()
                self.is_synced = True
            else:
                print('sync scan file system first')
                raise   

    def genSyncFolders(self):
        #assumed directories have been pre-hashed and walked
        #need to walk target side as well
        if(self.sourceFolderExists):
            #print('self.sourceFolder.items',self.sourceFolder.items)
            for i,item in enumerate(self.sourceFolder.items):
                #print(item)
                #print(item.dirEntryIndex)
                p = item.path
                #print(item.is_dir()
                if item.is_dir():
                    if not(any([i.sourcePath==p and i.targetPath==self.targetPath + '\\' + item.name for i in self.syncChildrenFolders])):
                        print('sync folder created',p,self.targetPath + '\\' + item.name)
                        s = SyncFolderInfoObject(p,self.targetPath + '\\' + item.name,autoPopulate,self.syncScanFolders,self.autoSync,self.genHashes,False,False)
                        self.syncChildrenFolders.append(s)
                        
        if(self.targetFolderExists):
            for i,item in enumerate(self.targetFolder.items):
                p = item.path
                if item.is_dir():
                    if not(any([i.sourcePath==p and i.targetPath==self.targetPath + '\\' + item.name for i in self.syncChildrenFolders])):
                        print('sync folder created',self.sourcePath + '\\' + item.name, p)
                        s = SyncFolderInfoObject(self.sourcePath + '\\' + item.name, p,autoPopulate,self.syncScanFolders,self.autoSync,self.genHashes,False,False)
                        self.syncChildrenFolders.append(s)
        
            self.is_scanned = True

    def genSyncLists(self):
        #assumed directories have been pre-hashed and walked
        #need to walk target side as well
        if(self.sourceFolderExists):
            #print('self.sourceFolder.items',self.sourceFolder.items)
            for i,item in enumerate(self.sourceFolder.items):
                #print(item)
                #print(item.dirEntryIndex)
                p = item.path
                if not item.is_dir():
                    target_file_name = self.targetPath + '\\' + item.name
                    print('>>>>>>>',target_file_name,os.path.exists(target_file_name))
                    if os.path.exists(target_file_name):
                        if item.hash != self.targetFolder.items[self.targetFolder.names.index(item.name)].hash:
                            self.s_update_list.append([p,target_file_name])
                        else:
                            self.s_synced_list.append([p,target_file_name])
                    else:
                        self.s_add_list.append([p,target_file_name])
            
                        
        if(self.targetFolderExists):
            for i,item in enumerate(self.targetFolder.items):
                p = item.path
                if not item.is_dir():
                    source_file_name = self.sourcePath + '\\' + item.name
                    print('>>>>>>>',source_file_name,os.path.exists(source_file_name))
                    if os.path.exists(source_file_name):
                        if item.hash != self.sourceFolder.items[self.sourceFolder.names.index(item.name)].hash:
                            self.t_update_list.append([p,source_file_name])
                        else:
                            self.t_synced_list.append([p,source_file_name])
                    else:
                        self.t_add_list.append([p,source_file_name])
        for i in self.syncChildrenFolders:
            i.genSyncLists()
            
            self.is_scanned = True

    def sync(self):
        #assumes populated, sync scanned
        pass
                    
        
    def syncToTarget(self,overwrite=False):
        preserve_mode=True
        preserve_times=True
        update=False
        for i in self.s_add_list:
            try:
                os.makedirs(os.path.dirname(i[1]))
            except FileExistsError:
                pass
            except FileNotFoundError:
                pass
            print('-----------copying-------------------',i[0],i[1])
            copy_file(i[0], os.path.dirname(i[1]), preserve_mode,preserve_times, update, verbose=True,dry_run=False)
        for i in self.syncChildrenFolders:
            i.syncToTarget()
            
    def syncToSource(self,overwrite='n'):
        for i in self.s_add_list:
            pass
            
    def getSourceFolderFileHashLists(self):
        sfDirFilePaths = []
        sfDirHashes = []
        if self.is_populated:
            if hasattr(self,'sourceFolder'):
                for i in self.sourceFolder.items:
                    if not i.is_dir():
                        sfDirFilePaths.append(i.path)
                        sfDirHashes.append(i.hash)
                for i in self.syncChildrenFolders:
                    result = i.getSourceFolderFileHashLists()
                    sfFilePaths, sfChildHashes = result[0],result[1]
                    sfDirFilePaths = sfDirFilePaths + sfFilePaths
                    sfDirHashes = sfDirHashes + sfChildHashes
        else:
            print("auto populate before calling getDirStructure")
            raise

        return sfDirFilePaths,sfDirHashes

    def getTargetFolderFileHashLists(self):
        tfDirFilePaths = []
        tfDirHashes = []
        if self.is_populated:
            if hasattr(self,'targetFolder'):
                for i in self.targetFolder.items:
                    if not i.is_dir():
                        tfDirFilePaths.append(i.path)
                        tfDirHashes.append(i.hash)
                for i in self.syncChildrenFolders:
                    #print('i-----------------------',str(i))
                    result = i.getTargetFolderFileHashLists()
                    tfFilePaths, tfChildHashes = result[0],result[1]
                    tfDirFilePaths =  tfDirFilePaths + tfFilePaths
                    tfDirHashes =  tfDirHashes + tfChildHashes
        
        else:
            print("auto populate before calling getDirStructure")
            raise

        return tfDirFilePaths,tfDirHashes

    def loadSourceFolderFileHashLists(self,sfDirFilePaths,sfDirHashes):
        #print(sfDirFilePaths,sfDirHashes)
        if self.is_populated:
            if hasattr(self,'sourceFolder'):
                for i in self.sourceFolder.items:
                    if not i.is_dir():
                        i.hash = sfDirHashes[sfDirFilePaths.index(i.path)]
                for i in self.syncChildrenFolders:
                    i.loadSourceFolderFileHashLists(sfDirFilePaths,sfDirHashes)
        else:
            print("auto populate before calling getDirStructure")
            raise

    def loadTargetFolderFileHashLists(self,tfDirFilePaths,tfDirHashes):
        #print(tfDirFilePaths,tfDirHashes)
        if self.is_populated:
            if hasattr(self,'targetFolder'):
                for i in self.targetFolder.items:
                    if not i.is_dir():
                        i.hash = tfDirHashes[tfDirFilePaths.index(i.path)]
                for i in self.syncChildrenFolders:
                    i.loadTargetFolderFileHashLists(tfDirFilePaths,tfDirHashes)
        else:
            print("auto populate before calling getDirStructure")
            raise
        
        
    def saveHashesToFile(self):
        result = self.getSourceFolderFileHashLists()
        sn,sh = result[0],result[1]
        result = self.getTargetFolderFileHashLists()
        tn,th = result[0],result[1]
        
        with open('sourceFileNames.'+os.path.basename(self.sourcePath)+'.txt','w') as f:
            for s in sn:
                f.write(s+'\n')
        with open('sourceHashes.'+os.path.basename(self.sourcePath)+'.txt','w') as f:
            for s in sh:
                f.write(s+'\n')
        with open('targetFileNames.'+os.path.basename(self.targetPath)+'.txt','w') as f:
            for s in tn:
                f.write(s+'\n')
        with open('targetHashes.'+os.path.basename(self.targetPath)+'.txt','w') as f:
            for s in th:
                f.write(s+'\n')

    def loadHashesFromFiles(self):
        sn,sh = [],[]
        tn,th = [],[]
        
        with open('sourceFileNames.'+os.path.basename(self.sourcePath)+'.txt','r') as f:
            data = '0'
            while data!='':
                data = f.readline()
                sn.append(data.removesuffix('\n'))
                
        if sn[-1] == '':
            sn = sn[0:-1]
            
        with open('sourceHashes.'+os.path.basename(self.sourcePath)+'.txt','r') as f:
            data = '0'
            while data!='':
                data = f.readline()
                sh.append(data.removesuffix('\n'))
                
        if sh[-1] == '':
            sh = sh[0:-1]
            
        with open('targetFileNames.'+os.path.basename(self.targetPath)+'.txt','r') as f:
            data = '0'
            while data!='':
                data = f.readline()
                tn.append(data.removesuffix('\n'))
                
        if tn[-1] == '':
            tn = tn[0:-1]
            
        with open('targetHashes.'+os.path.basename(self.targetPath)+'.txt','r') as f:
            data = '0'
            while data!='':
                data = f.readline()
                th.append(data.removesuffix('\n'))
                
        if th[-1] == '':
            th = th[0:-1]

        self.loadSourceFolderFileHashLists(sn,sh)
        self.loadTargetFolderFileHashLists(tn,th)

autoPopulate=True
syncScanFolders=True

genHashes=True
loadHashes=False
saveHashes=True

autoSync=False


#-------------
#test_folder = SyncFolderInfoObject('G:\\pv','D:\\pv',autoPopulate,syncScanFolders,autoSync,genHashes,loadHashes,saveHashes)
test_folder = SyncFolderInfoObject('G:\\docs\\notes','J:\\docs\\notes',autoPopulate,syncScanFolders,autoSync,genHashes,loadHashes,saveHashes)

test_folder.genSyncLists()
test_folder.syncToTarget()


#with open('test.txt','w') as f:
#    f.write(str(listify(test_folder)).replace('[','\n\t['))


