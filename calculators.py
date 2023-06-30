# felix zimmermann, github.com/fzimmermann89 for beamtime kuschel2023


import numpy as np


class topk():
    def __init__(self, k):
        """
        a priority queue with size=k
         - keeps the top k elements
        
        add elements via put
        get topk via get
        """
        self._storage = []
        self._k = k
        
    def add(self, value, data=None):
        """
        add an element
        Parameters
        ------
        value: value to sort by
        data: data to save. if None, use value
        """
        if data is None:
            data = (value,)
        self._storage.append((value, data))
        self._storage = sorted(self._storage, reverse=True)[:self._k]

    def get(self):
        return [el[1] for el in self._storage]
    


class Histogrammer:
    def __init__(self, bins, range):
        """
        Calculates Histogramms with the same bins
        """
        self.bins = bins
        self.range = range

    def __call__(self,data):
        return np.histogram(data, bins=self.bins, range=self.range)[0]

    def edges(self):
        return np.histogram_bin_edges(np.zeros(0), bins=self.bins, range=self.range)

    def centers(self):
        edges = self.edges()
        centers = (edges[1:] + edges[:-1]) / 2
        return centers

    
class RangeCounter():
    def __init__(self, low:float=-np.inf, high:float=np.inf):
        """
        Counts occurances of low<value<high
        """
        self.low=low
        self.high=high
        
    def __call__(self, data):
        data = np.asarray(data)
        counts =np.sum((data>self.low) & (data<self.high))
        return counts

    
class NoiseCutter():
    def __init__(self, threshold=1000, fill_value=0.):
        """
        Cuts values below threshold.
        if set_to_nan, these are set to nan, othervi
        """
        self.threshold = threshold
        self.fill_value=fill_value
    
    def __call__(self, image):
        ret = np.copy(image)
        ret[ret<self.threshold] = self.fill_value
        return ret