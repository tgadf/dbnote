""" Merge Search Artist Results """

__all__ = ["MergeSearchArtist"]

from musicdb import getdbio
from pandas import DataFrame, Series
from utils import header

class MergeSearchArtist:
    def __repr__(self):
        return f"MergeSearchArtist(db={self.db})"
        
    def __init__(self, db, **kwargs):
        self.db = db
        header(self.__repr__(), width=125)

    def merge(self, newData: DataFrame, **kwargs) -> 'None':
        test = kwargs.get('test', False)
        dbio = getdbio(self.db)
        assert isinstance(newData, (Series, DataFrame)), f"newData [{type(newData)}] is not a Series/DataFrame"
        prevData = dbio.rdio.getData("SearchArtist")
        assert isinstance(prevData, (Series, DataFrame)), f"prevData [{type(prevData)}] is not a Series/DataFrame"
                                  
        nPrevResults = prevData.shape[0]
        print(f"Found {nPrevResults} Previously Known Results")
        
        nSearches = len(searchArtistRecord.recordData['Data'])
        nResults = newData.shape[0]
        print(f"Found {nSearches} Searches")
        print(f"Found {nResults} Results")
        nDuplicates = newData.index.duplicated().sum()
        print(f"Found {nDuplicates} Duplicate Results")
        newData = newData[~newData.index.duplicated()]
        
        newResults = newData[~newData.index.isin(prevData.index)]
        nNewResults = newResults.shape[0]
        rResultsPerSearch = nResults/nSearches
        rNewResultsPerSearch = nNewResults / nSearches
        print(f"Found {nNewResults} New Results")
        print(f"  ==> {rResultsPerSearch:.2f} All Results / Search")
        print(f"  ==> {rNewResultsPerSearch:.2f} New Results / Search")

        if test is True:
            print("Only testing. Will not save anything")
            return
        
        if newResults.shape[0] > 0:
            searchArtistsData = concat([prevData, newResults])
            nSearchArtistsData = searchArtistsData.shape[0]
            print(f"Saving {nSearchArtistsData} Data ... ", end="")
            dbio.rdio.saveData("SearchArtist", data=searchArtistsData)
            print("Done")
        else:
            print("Nothing new to save.")
        searchArtistRecord.initData(force=True)