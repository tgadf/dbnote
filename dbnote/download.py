""" Useful Classes For Downloading Music DB Data """

__all__ = ["DownloadRecord"]

from dbmaster import MasterPersist
from dbbase import MusicDBDir, MusicDBData
from utils import header
from pandas import Series, DataFrame


class DownloadRecord:
    def __repr__(self):
        return f"DownloadRecord(db={self.db}, name={self.name}, rTypes={self.rTypes})"
        
    def __init__(self, db, name, rTypes: list, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        self.db = db
        self.name = name
        self.rTypes = rTypes
        self.dTypes = (dict, Series, DataFrame, bytes)
        self.dTypesIO = (dict, Series, DataFrame)
        
        mper = MasterPersist()
        dbpath = MusicDBDir(mper.getDBPath(db))
        records = {}

        if "Index" in rTypes:
            fname = f"{db}-{name}-Index"
            records["Index"] = MusicDBData(path=dbpath, fname=fname)

        if "Data" in rTypes:
            fname = f"{db}-{name}-Data"
            records["Data"] = MusicDBData(path=dbpath, fname=fname)
            
        fname = f"{db}-{name}-Error"
        records["Error"] = MusicDBData(path=dbpath, fname=fname)

        self.records = records
        self.recordData = None

        print(self.__repr__())

    ################################################################################
    # Info
    ################################################################################
    def getSize(self, val):
        size = "-"
        if isinstance(val, dict):
            size = len(val)
        elif isinstance(val, (Series, DataFrame)):
            size = val.shape[0]
        elif val is None:
            size = "N/A"
        return size
        
    def info(self):
        for rType, record in self.records.items():
            key = f"{self.name} {rType}"
            val = record.get()
            size = self.getSize(val)
            print(f"  {key: <20}: {size}")

    ################################################################################
    # File I/O
    ################################################################################
    def initData(self, force=False):
        header(f"Initializing {self.name}", width=125)
        rType = "Data"
        record = self.records.get(rType)
        if not isinstance(record, MusicDBData):
            print("No data record to initialize")
            return
        if force is True:
            print(f"  Initializing {rType: <6} ... ", end="")
            record.save(data={})
            self.load(verbose=False)
            print("Done")
        else:
            print(f"  Not initializing {rType} because forece is False")
        
    def init(self, force=False):
        header(f"Initializing {self.name}", width=125)
        for rType, record in self.records.items():
            if force is True:
                print(f"  Initializing {rType: <6} ... ", end="")
                record.save(data={})
                print("Done")

    def load(self, verbose=True):
        if verbose is True:
            header(f"Loading {self.name}", width=125)
        self.recordData = {}
        for rType, record in self.records.items():
            if verbose is True:
                print(f"  Loading {rType: <6} ... ", end="")
            self.recordData[rType] = record.get()
            assert isinstance(self.recordData[rType], self.dTypes), f"{rType} Records are not a dict"
            size = self.getSize(self.recordData[rType])
            if verbose is True:
                print(f"Done. Found {size} Records")

    def save(self, verbose=True):
        assert isinstance(self.recordData, dict), "Records are not loaded. Will not save data"
        if verbose is True:
            header(f"Saving {self.name}", width=125)
        for rType, rData in self.recordData.items():
            assert isinstance(rData, self.dTypes), f"{rType: <6} Records are not a dict"
            if verbose is True:
                print(f"  Saving {rType} [{len(rData)}] ... ", end="")
            self.records[rType].save(data=rData)
            if verbose is True:
                print("Done")

    ################################################################################
    # Get Records
    ################################################################################
    def getRecords(self, rType=None):
        if self.recordData is None:
            self.load()
        retval = self.recordData.get(rType) if isinstance(rType, str) else self.recordData
        assert retval is not None, "Return data [getRecords] is None"
        return retval
        
    def getIndex(self, rType=None):
        rData = self.getRecords("Index")
        retval = rData if isinstance(rData, dict) else None
        assert retval is not None, "Return data [getIndex] is None"
        return retval
        
    def getData(self, rType=None):
        rData = self.getRecords("Data")
        retval = rData if isinstance(rData, dict) else None
        assert retval is not None, "Return data [getData] is None"
        return retval
        
    def getError(self, rType=None):
        rData = self.getRecords("Error")
        retval = rData if isinstance(rData, dict) else None
        assert retval is not None, "Return data [getError] is None"
        return retval

    def isKnown(self, index: str) -> 'bool':
        if not isinstance(self.recordData, dict):
            self.load(verbose=False)
        assert isinstance(self.recordData.get('Index'), (dict, Series)), "Index records are not available"
        assert isinstance(self.recordData.get('Error'), (dict, Series)), "Error records are not available"
        idxVal = self.recordData['Index'].get(index)
        errVal = self.recordData['Error'].get(index)
        retval = any([obj is True for obj in [idxVal, errVal]])
        return retval
    
    def numKnown(self) -> 'int':
        if not isinstance(self.recordData, dict):
            self.load(verbose=False)
        assert isinstance(self.recordData.get('Index'), (dict, Series)), "Index records are not available"
        assert isinstance(self.recordData.get('Error'), (dict, Series)), "Error records are not available"
        total = set(self.recordData['Index'].keys()).union(set(self.recordData['Error'].keys()))
        retval = len(total)
        return retval

    def isError(self, index: str) -> 'bool':
        if not isinstance(self.recordData, dict):
            self.load(verbose=False)
        assert isinstance(self.recordData.get('Error'), (dict, Series)), "Error records are not available"
        errVal = self.recordData['Error'].get(index)
        retval = errVal is True
        return retval

    ################################################################################
    # Set Records
    ################################################################################
    def setError(self, index):
        if not isinstance(self.recordData, dict):
            self.load(verbose=False)
        assert isinstance(self.recordData.get('Error'), dict), "Error records are not available"
        self.recordData['Error'][index] = True

    def setIndex(self, index):
        if not isinstance(self.recordData, dict):
            self.load(verbose=False)
        assert isinstance(self.recordData.get('Index'), dict), "Index records are not available"
        self.recordData['Index'][index] = True

    def setData(self, index, data):
        if not isinstance(self.recordData, dict):
            self.load(verbose=False)
        assert isinstance(self.recordData.get('Data'), dict), "Data records are not available"
        self.recordData['Index'][index] = True
        self.recordData['Data'][index] = data