# zimmf for beamtime kuschel2023

import numpy as np


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
        counts =np.sum((data>self.low) & (data<self.high))
        return counts
        