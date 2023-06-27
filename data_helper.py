import dbpy
import stpy
import numpy as np
import re
from typing import List, Dict
from collections import namedtuple


def getNewestRun(bl: int = 3):
    """
    returns newest run number for the beamline
    Parameters
    ----------
    input: beamline as integer

    output: runnumber as integer
    """
    return dbpy.read_runnumber_newest(bl)


def getDetectorList(bl: int = 3, run: int = -1):
    """
    returns available detector list for beamline and  run number
    Detectors are cameras like the MPCCD

    Parameters
    ----------
    bl: beamline as integer
    run: -1 to use newest

    output: tuple list of detector names
    """
    if run == -1:
        run = getNewestRun(bl)
    return dbpy.read_detidlist(bl, getNewestRun(bl))


def getEquipmentList():
    """
    returns available list of equipment

    Parameters
    ----------
    None

    output: tuple list of equipment names
    """
    return dbpy.read_equiplist()


def getHighTag(bl: int = 3, run: int = -1):
    """
    returns high tag value for particular beamline and run number

    Parameters
    ----------
    bl: beamline as integer
    run: -1 to use newest

    output: high tag value as integer
    """
    if run < 0:
        run = getNewestRun(bl) + 1 + run
    return dbpy.read_hightagnumber(bl, run)


class LazyImage:
    def __init__(self, tag, obj, buff):
        self._tag = tag
        self._obj = obj
        self._buff = buff

    def get(self):
        self._obj.collect(self._buff, self._tag)
        data = self._buff.read_det_data(0)
        return data

    def __array__(self):
        return self.get()

    def __repr__(self):
        return f"LazyImage at tag {self._tag}.\n   Use np.array(lazyimage) or lazyimage.get() to get the data."


class Detector:
    def __init__(self, detID: str, bl: int = 3, run: int = -1, lazy=True):
        """
        A sacla detector at a specific run.

        Parameters
        ----------
        detID: 'MPCCD-1N0-M06-002' or similiar
        bl: beamline number
        run: run number. if -1, use newest
        lazy: load image only on access. might not be threadsafe
        """
        if run < 0:
            run = getNewestRun(bl) + 1 + run
        self._taglist = dbpy.read_taglist_byrun(bl, run)
        self._obj = stpy.StorageReader(detID, bl, (run,))
        self._buff = stpy.StorageBuffer(self._obj)
        self._detID = detID
        self._run = run
        self.lazy = lazy

    def __len__(self):
        return len(self._taglist)

    def __repr__(self):
        return f"Detector {self._detID} at run {self._run}"

    def __getitem__(self, idx):
        tag = self._taglist[idx]
        if self.lazy:
            return LazyImage(tag, self._obj, self._buff)
        self._obj.collect(self._buff, tag)
        data = self._buff.read_det_data(0)
        return data


def searchEquipmentList(pattern: str):
    """
    searches for a regex pattern in the equipment list
    and returns all matches.

    Parameters
    ------
    pattern: regex pattern

    Returns
    ------
    list of matching strings


    """
    equipment = getEquipmentList()
    pattern = re.compile(pattern)
    matches = [equip for equip in equipment if pattern.search(equip)]
    return matches


def getEquip(equipment_name: str, tags: List, hightag):
    """
    returns data from detector for specified tags, hightag

    Parameters
    ------
        equipment_name: equipment name
        list: tuple of integer values
        hightag: high tag integer value

    Returns
    -------
    detector value accross tags as float
    """
    if run == -1:
        run = getNewestRun(bl)
    hightag = getHighTag(bl, run)
    equipVals = dbpy.read_syncdatalist_float(equip, hightag, tags)


class DBReader:
    def __init__(self, keys: Dict, bl: int = 3, run: int = -1):
        """
        A sacla databse values at a specific run.

        Parameters
        ----------
        keys: dict. {name:info}
            info can either be:
                string: name of the database object
                tuple/list:
                    name:str, calibration_factor:float) : calibrate by multipylication with the factor
                    name:str, calibration_function:callable: apply calibration function to each valuue
        bl: beamline number
        run: run number. if -1, use newest


        Returns a named tuple of the database entrys named by the kezs in keys.
        """
        if run < 0:
            run = getNewestRun(bl) + 1 + run
        self._taglist = dbpy.read_taglist_byrun(bl, run)
        self._keys = keys
        hightag = getHighTag(bl, run)
        data = {}
        for name, info in keys.items():
            if isinstance(info, str):
                key, calibrate = info, lambda x: x
            elif isinstance(info, (list, tuple)) and len(info) == 2 and isinstance(info[0], str) and callable(info[1]):
                key, calibrate = info
            elif (
                isinstance(info, (list, tuple))
                and len(info) == 2
                and isinstance(info[0], str)
                and isinstance(info[1], float)
            ):
                key = info[0]
                calibrate = lambda x: x * info[1]
            else:
                raise ValueError("info must be a string or a tuple of string and float or callable")
            raw = dbpy.read_syncdatalist_float(key, hightag, self._taglist)
            data[name] = calibrate(np.array(raw))
        data["tag"] = self._taglist
        self._data = data
        self._run = run
        self._returntype = namedtuple("DBValues", data.keys())

    def __len__(self):
        return len(self._taglist)

    def __repr__(self):
        return f"DBReader {self._keys} at run {self._run}"

    def __getitem__(self, idx):
        tag = self._taglist[idx]
        data = {key: value[idx] for key, value in self._data.items()}
        return self._returntype(**data)


class Run:
    def __init__(self, detector_keys:Dict, database_keys:Dict, bl:int=3, run:int=-1):
        """
        A Sacla run
        
        Parameters
        -------
        detector_keys: dict of name:sacla_internal_name of mpccd detectors
        database_keys: dict of parameters to get from database, see DBReader for format
        bl: beamline
        run: run to use. if negative, relative from newest
        
        Usage
        ------
        shot=Run(...)[0] 
        or 
            for shot in Run(...):
                ...
        
        each shot is a namedtuple.
        """
        self.detectors = {name: Detector(detID, bl, run, lazy=True) for name, detID in detector_keys.items()}
        self.db = DBReader(database_keys, bl, run)
        self._returntype = namedtuple(
            "Shot", field_names=list(self.detectors.keys()) + list(self.db._returntype._fields)
        )

    def __getitem__(self, idx):
        detdata = {name: det[idx] for name, det in self.detectors.items()}
        dbdata = self.db[idx]._asdict()
        return self._returntype(**detdata, **dbdata)
