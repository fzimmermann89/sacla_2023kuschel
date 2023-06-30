# felix zimmermann, github.com/fzimmermann89 for beamtime kuschel2023

import dbpy
import stpy
import numpy as np
import re
from typing import List, Dict, Union #,Literal missing in 3.7
from collections import namedtuple
import datetime
from functools import lru_cache
import accumulators
from pathlib import Path

### Basic Helper functions
def parseDate(date):
    if isinstance(date, datetime.datetime):
        return date
    if isinstance(date, str):
        return datetime.datetime.fromisoformat(date)
    if isinstance(date,float):
        return datetime.datetime.fromtimestamp(date)
    if isinstance(date, datetime.date):
        return datetime.datetime.combine(date,datetime.time())
    if isinstance(date, datetime.time):
        return datetime.datetime.combine(date,datetime.today())
    else:
        raise ValueError(f"{date} is not convertible to date")

def getRunTime(bl=3, run=-1):
    """
    get (start, end)-time as list of datetime
    if run is negative, use relative from last run
    """
    if run < 0:
        run = getNewestRun(bl) + 1 + run
    return [datetime.datetime.fromtimestamp(el) for el in (dbpy.read_starttime(bl, run),dbpy.read_stoptime(bl, run))]

def getNewestRun(bl: int = 3):
    """
    returns newest run number for the beamline
    Parameters
    ----------
    bl: beamline as integer

    output: runnumber as integer
    """
    return dbpy.read_runnumber_newest(bl)


def getTags(bl=3, run=-1):
    """
    get a list of tags (i.e. shot identifiers) for a run
    
    Returns
    ------
    list
    """
    if run < 0:
            run = getNewestRun(bl) + 1 + run
    
    return dbpy.read_taglist_byrun(bl, run)


def getHighTag(bl: int = 3, run: int = -1):
    """
    returns high tag value for particular beamline and run number

    Parameters
    ----------
    bl: beamline as integer
    run: -1 to use newest

    Returns
    ------
    high tag value as integer
    """
    if run < 0:
        run = getNewestRun(bl) + 1 + run
    return dbpy.read_hightagnumber(bl, run)


def getDetectorList(bl: int = 3, run: int = -1):
    """
    returns available detector list for beamline and  run number
    Detectors are cameras like the MPCCD

    Parameters
    ----------
    bl: beamline as integer
    run: -1 to use newest

    Returns
    ------
    tuple list of detector names
    """
    if run < 0:
        run = getNewestRun(bl) + 1 + run
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



def getDetectorImage(detID:str, taglist=None, bl=3, run=-1, in_ev=True):
    """
    reads one or multiple detector images
    Parameters
    ---------
    detID: name of detector
    taglist: list of tags to get images for, single tag, or None (all images of run)
    bl: beamline
    run: run nr, negative is relative to newest
    in_ev: convert to ev using the gain
    """
    if run < 0:
            run = getNewestRun(bl) + 1 + run
    if taglist is None:
        taglist = getTags(bl, run=run)
    if isinstance(taglist, int):
        taglist = [taglist]
    
    obj = stpy.StorageReader(detID, bl, (run,))
    buff = stpy.StorageBuffer(obj)
    obj.collect(buff, taglist)
    data = buff.read_det_data(0)
    
    if in_ev:
        info = buff.read_det_info(0) 
        evPerAdu=info["mp_absgain"] * 3.65
        data = data * evPerAdu
    return data


def getDetEvPerADU(detID, bl=3, run=-1, tag=None):
    """
    reads the absgain * 3.65 ev/adu
    to get the conversion factor
    """
    info=getDetInfo(detID, bl=3, run=-1, tag=None)
    return info["mp_absgain"] * 3.65 


def getDetInfo(detID, bl=3, run=-1, tag=None):
    """
    read Detector Info
    """
    if run < 0:
        run = getNewestRun(bl) + 1 + run
    if tag is None:
        taglist = getTags(bl, run=run)[0]

    obj = stpy.StorageReader(detID, bl, (run,))
    buff = stpy.StorageBuffer(obj)
    obj.collect(buff, taglist)
    info = buff.read_det_info(0) 
    return info


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
    return  dbpy.read_syncdatalist_float(equipment_name, hightag, tags)

    
def getEquipForRun(equipment_name: str, bl=3, run=-1):
    """
    returns data from detector for specified tags, hightag

    Parameters
    ------
        equipment_name: equipment name
        bl: beamline
        run: run

    Returns
    -------
    detector value accross tags as np.array
    """
    if run < 0:
            run = getNewestRun(bl) + 1 + run
    tags = getTags(bl, run=run)
    hightag = getHighTag(bl, run)
    return dbpy.read_syncdatalist_float(equipment_name, hightag, tags)
    


class LazyImage(np.lib.mixins.NDArrayOperatorsMixin):
    """
    an image that will only be loaded on first access
    use .get() to get the data.
    """
    def __init__(self, tag, obj, buff, dark, ev_per_adu):
        self._tag = tag
        self._obj = obj
        self._buff = buff
        self._data = None
        self._dark = dark
        self._ev_per_adu = ev_per_adu

    def get(self):
        """
        get the image
        """
        if self._data is None:
            self._obj.collect(self._buff, self._tag)
            data = self._buff.read_det_data(0)
            if self._dark is not None:
                data = data - self._dark
                self._dark = None
            self._data = self._ev_per_adu * data
        return self._data

    def __array__(self):
        return self.get()
    
    def __repr__(self):
        return f"LazyImage at tag {self._tag}.\n   Use np.array(lazyimage) or lazyimage.get() to get the data."

    
    
##### More fancy classes ######

class Detector:
    def __init__(self, detID: str, bl: int = 3, run: int = -1, dark: np.ndarray = None, ev_per_adu: Union[float,str] = 1.0, lazy=False):
        """
        A sacla detector at a specific run.

        Parameters
        ----------
        detID: 'MPCCD-1N0-M06-002' or similiar
        bl: beamline number
        run: run number. if -1, use newest
        dark: an numpy array (in ADU) to subtract or None
        ev_per_adu: "auto" or value. images is scaled by this factor before returning auto gets the value automatically from the gain.
        lazy: load image only on access. might not be threadsafe
        """
        if run < 0:
            run = getNewestRun(bl) + 1 + run
        self._taglist = dbpy.read_taglist_byrun(bl, run)
        self._obj = stpy.StorageReader(detID, bl, (run,))
        self._buff = stpy.StorageBuffer(self._obj)
        if isinstance(ev_per_adu,str):
            if ev_per_adu == "auto":
                self._obj.collect(self._buff, self._taglist[0])
                ev_per_adu =  self._buff.read_det_info(0)["mp_absgain"] * 3.65  
            else:
                raise ValueError("if ev_per_adu is a string, only 'auto' is allowed")
            
        self._ev_per_adu = ev_per_adu
        self._dark = dark
        self._detID = detID
        self._run = run
        self.lazy = lazy

    def __len__(self):
        return len(self._taglist)

    def __repr__(self):
        return f"Detector {self._detID} at run {self._run}"
    
    @lru_cache(maxsize=1)
    def __getitem__(self, idx):
        if idx>=len(self._taglist):
            raise IndexError
        tag = self._taglist[idx]
        if self.lazy:
            return LazyImage(tag, self._obj, self._buff, dark=self._dark, ev_per_adu=self._ev_per_adu)
        self._obj.collect(self._buff, tag)
        data = self._buff.read_det_data(0)
        if self._dark is not None:
            data = data - self._dark
        data = self._ev_per_adu * data
        return data

    
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
            elif isinstance(info, (list, tuple)) and len(info) == 2 and isinstance(info[0], str) and isinstance(info[1], float):
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
        if idx>=len(self._taglist):
            raise IndexError
        tag = self._taglist[idx]
        data = {key: value[idx] for key, value in self._data.items()}
        return self._returntype(**data)
    
    @property
    def data(self):
        return self._returntype(**self._data)


class Run:
    def __init__(
        self, detector_keys: Dict, database_keys: Dict, detector_dark_paths: Dict = None, bl: int = 3, run: int = -1, lazy:bool=True, detectors_in_ev = True
    ):
        """
        A Sacla run

        Parameters
        -------
        detector_keys: dict of name:sacla_internal_name of mpccd detectors
        database_keys: dict of parameters to get from database, see DBReader for format
        detector_dark_paths: dict of folders in which darkfiles are stored for each detector. darkfiles have to be named matching "*_{timestamp}.np?".
        bl: beamline
        run: run to use. if negative, relative from newest
        lazy: load det images lazyly on first access
        detectors_in_ev: detectors are returned in ev(ish)
        

        Usage
        ------
        shot=Run(...)[0]
        or
            for shot in Run(...):
                ...

        each shot is a namedtuple.
        """
        self.detectors = {}
        for name, detID in detector_keys.items():
            if detector_dark_paths is not None and name in detector_dark_paths and detector_dark_paths[name] is not None:
                darkfilename = find_closest_darkfile(detector_dark_paths[name], bl=bl,run=run)
                if darkfilename is None:
                    print("No dark found in folder!")
                    dark = None
                else:
                    dark = np.load(darkfilename)
            else:
                dark = None
            det = Detector(detID, bl=bl, run=run, dark=dark, lazy=lazy, ev_per_adu="auto" if detectors_in_ev else 1.0)
            self.detectors[name] = det
        self.db = DBReader(database_keys, bl, run)
        self._returntype = namedtuple("Shot", field_names=list(self.detectors.keys()) + list(self.db._returntype._fields))
        self.__dict__.update(**self.db.data._asdict())
    def __getitem__(self, idx):
        if idx>=len(self):
            raise IndexError
        detdata = {name: det[idx] for name, det in self.detectors.items()}
        dbdata = self.db[idx]._asdict()
        return self._returntype(**detdata, **dbdata)
    
    def __len__(self):
        if self.db is not None:
            return len(self.db)
        if self.detectors is not None and len(self.detectors)>0:
            return len(self.detectors[0])
        else:
            return 0
    

def find_closest_darkfile(path,bl:int=3,run:int=-1):
    """
    darkfiles have to be named *_{timestamp}.np?"
    returns filename of file that has timestime
    closest to the middle of the run
    
    Parameters:
    --------
        path: path to look
        run: run number, negative to be relative to last run
        bl: beamline
    """
    start,end = (el.timestamp() for el in getRunTime(bl,run))
    center = (start+end)/2 #middle of the run
    files_and_times=[]
    for file in (Path(path).rglob("*_*.np?")):
        try:
            time = float(file.stem.split("_")[-1])
            files_and_times.append((time,file))
        except (ValueError, IndexError):
            continue
    if len(files_and_times)==0:
        #nothing found
        darkfile= None
    else:
        #find closest darkfile to middle of the run
        darkfile=sorted(files_and_times,key=lambda el:abs(el[0]-center))[0][1]
    return darkfile



def to_dict(run,shots_taken=None, **kwargs):
    """
    convert run and **kwargs to a dict of arrays.
    for accumulators, the value is used
    shots_taken are the good shots, the database values from run are subset on these
    """
    ret = {}
    if shots_taken is None:
        ret.update(**run.db.data._asdict())
    else:
        for name, value in run.db.data._asdict().items():
            try:
                ret[name]=np.array(value)[shots_taken]
            except Exception as e:
                print("could not convert", name, e)
    for name, value in kwargs.items():
        try:
            if isinstance(value,accumulators.Accumulator):
                ret[name] = value.value
            else:
                ret[name] = value
        except Exception as e:
            print("could not convert", name, e)
    return ret


def read_data_generator(path, minrun=0, maxrun=9313254, get_run_from_filename=True):
    """
    reads cached results, named data*
    if get_run_from_filename, the filename is used as a fast run number filter
    the filename shoud be *run{runnr}.npz for that to work
    """
    path=Path(path)
    files=path.glob(f"data*.npz")
    ret={}
    for file in sorted(list(files)):
        if get_run_from_filename:
            runnr = int(file.stem.split("run")[-1])
            if not (minrun<=runnr and  runnr<=maxrun):
                continue
        f=np.load(file)
        runnr=int(f["runNR"])
        if minrun<=runnr and  runnr<=maxrun:
            yield f