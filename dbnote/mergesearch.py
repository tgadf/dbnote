""" Merge Search Artist Results """

__all__ = ["MergeSearchArtist"]

from musicdb import getdbio
from pandas import DataFrame, Series, concat
from utils import header, FileInfo, getFile
from .download import DownloadRecord


class MergeSearchArtist:
    def __repr__(self):
        return f"MergeSearchArtist(db={self.db})"
        
    def __init__(self, db, **kwargs):
        self.db = db
        header(self.__repr__(), width=125)
    
    ##########################################################################################
    # Local Init
    ##########################################################################################
    def localInit(self):
        _ = getdbio(db=self.db, local=True, mkDirs=True)
        self.copyFromGlobal(force=True)

    ##########################################################################################
    # Search Artist I/O
    ##########################################################################################
    def getSearchArtistData(self, dbio):
        return dbio.rdio.getData("SearchArtist")
        
    def saveSearchArtistData(self, dbio, data):
        dbio.rdio.saveData("SearchArtist", data=data)
    
    def getLocalSearchArtistData(self):
        return self.getSearchArtistData(getdbio(db=self.db, local=True))

    def saveLocalSearchArtistData(self, data):
        self.saveSearchArtistData(getdbio(db=self.db, local=True), data)

    def getGlobalSearchArtistData(self):
        return self.getSearchArtistData(getdbio(db=self.db, local=False))
        
    def saveGlobalSearchArtistData(self, data):
        self.saveSearchArtistData(getdbio(db=self.db, local=False), data)
    
    ##########################################################################################
    # Local/Global Artist I/O
    ##########################################################################################
    def createTempLocalCopy(self):
        print("  ==> Creating copy of local SearchArtist data")
        dbioLocal = getdbio(db=self.db, local=True)
        fname = dbioLocal.rdio.getFilename("SearchArtist")
        tmpname = FileInfo(fname.str.replace(".p", ".tmp.p"))
        fname.cpFile(tmpname, debug=False)
        data = getFile(tmpname)
        assert isinstance(data, (Series, DataFrame)), 'Corrupt local file!!!'
        print(f"  ==> Created copy of local SearchArtist data with {data.shape} shape")
        
    def copyFromLocal(self, force=False):
        data = self.getLocalSearchArtistData()
        print(f"New Local Shape:  {data.shape}")
        dataGlobal = self.getGlobalSearchArtistData()
        print(f"Old Global Shape: {dataGlobal.shape}")
        if force is True:
            self.saveGlobalSearchArtistData(data=data)
        else:
            print("Only testing. Will not copy Search Artist From Local to Global")
            return

        newdata = self.getGlobalSearchArtistData()
        print(f"New Global Shape: {newdata.shape}")

    def copyFromGlobal(self, force=False):
        data = self.getGlobalSearchArtistData()
        if force is True:
            self.saveLocalSearchArtistData(data=data)
        else:
            print("Only testing. Will not copy Search Artist From Global to Local")
            return
            
    def mergeLocal(self, searchArtistRecord: DownloadRecord, newData: DataFrame, **kwargs) -> 'None':
        self.createTempLocalCopy()
        test = kwargs.get('test', False)
        assert isinstance(newData, (Series, DataFrame)), f"newData [{type(newData)}] is not a Series/DataFrame"
        nResults = newData.shape[0]
        if nResults == 0:
            print("No new results. Returning.")
            return
        
        nSearches = len(searchArtistRecord.getData())
        if nSearches == 0:
            print("No new results. Returning.")
            return
        
        prevData = self.getLocalSearchArtistData()
        assert isinstance(prevData, (Series, DataFrame)), f"prevData [{type(prevData)}] is not a Series/DataFrame"
        nPrevResults = prevData.shape[0]
        print(f"Found {nSearches} Searches")
        print(f"Found {nResults} Results")
        nDuplicates = newData.index.duplicated().sum()
        print(f"Found {nDuplicates} Duplicate Results")
        newData = newData[~newData.index.duplicated()]
        
        newResults = newData[~newData.index.isin(prevData.index)]
        nNewResults = newResults.shape[0]
        rResultsPerSearch = nResults / nSearches
        rNewResultsPerSearch = nNewResults / nSearches
        
        print(f"Found {nPrevResults} Previously Known Results")
        print(f"Found {nNewResults} New Results")
        print(f"  ==> {rResultsPerSearch:.2f} All Results / Search")
        print(f"  ==> {rNewResultsPerSearch:.2f} New Results / Search")

        searchArtistsData = concat([prevData, newResults])
        nSearchArtistsData = searchArtistsData.shape[0]
        
        if test is True:
            print(f"Found {nSearchArtistsData} Total Results")
            print("Only testing. Will not save anything")
            return
        
        if newResults.shape[0] > 0:
            print(f"Saving {nSearchArtistsData} Data ... ", end="")
            self.saveLocalSearchArtistData(data=searchArtistsData)
            print("Done")
            
            data = self.getLocalSearchArtistData()
            assert isinstance(data, (Series, DataFrame)), 'Corrupt local file!!!'
            
            searchArtistRecord.initData(force=True)
        else:
            print("Nothing new to save.")
            searchArtistRecord.initData(force=True)