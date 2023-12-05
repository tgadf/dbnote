""" Useful Classes For Known Music DB Data """

__all__ = ["KnownRecord"]

from dbmaster import MasterPersist
from dbbase import MusicDBDir, MusicDBData
from utils import header
from pandas import Series, DataFrame


class KnownRecord:
    def __repr__(self):
        return f"DownloadRecord(db={self.db}, name={self.name})"
        
    def __init__(self, db, name, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        self.db = db
        self.name = name
        self.dTypes = (dict, Series, DataFrame, bytes)
        self.dTypesIO = (dict, Series, DataFrame)
        
        mper = MasterPersist()
        dbpath = MusicDBDir(mper.getDBPath(db))
        records = {}

        fname = f"{db}-{name}-Data"
        records["Data"] = MusicDBData(path=dbpath, fname=fname)
            
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

    def save(self):
        assert isinstance(self.recordData, dict), "Records are not loaded. Will not save data"
        header(f"Saving {self.name}", width=125)
        for rType, rData in self.recordData.items():
            assert isinstance(rData, self.dTypes), f"{rType: <6} Records are not a dict"
            print(f"  Saving {rType} [{len(rData)}] ... ", end="")
            self.records[rType].save(data=rData)
            print("Done")

    ################################################################################
    # Get Records
    ################################################################################
    def getData(self, rType=None):
        if not isinstance(self.recordData, dict):
            self.load(verbose=False)
        rData = self.recordData.get('Data')
        retval = rData if isinstance(rData, dict) else None
        assert retval is not None, "Return data [getData] is None"
        return retval

    ################################################################################
    # Set Records
    ################################################################################
    def setData(self, data):
        if not isinstance(self.recordData, dict):
            self.load(verbose=False)
        assert isinstance(data, dict), "Data is not a dict"
        self.recordData['Data'] = data
        
    def mergeData(self, data):
        assert isinstance(data, dict), "data is not a dict"
        if not isinstance(self.recordData, dict):
            self.load(verbose=False)
        assert isinstance(self.recordData.get('Data'), dict), "Data records are not available"
        self.recordData['Data'] = self.recordData['Data'] | data
        