# -*- coding: utf-8 -*-
# Copyright 2017 The PyCrystEM developers
#
# This file is part of PyCrystEM.
#
# PyCrystEM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyCrystEM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyCrystEM.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

from hyperspy.api import roi
from hyperspy.signals import BaseSignal, Signal1D, Signal2D

from pycrystem.utils.expt_utils import *

"""
Signal class for diffraction vectors.
"""

def _calculate_norms(z):
    norms = []
    #print(z)
    for i in z[0]:
        norms.append(np.linalg.norm(i))
    return np.asarray(norms)


class DiffractionVectors(BaseSignal):
    _signal_type = "diffraction_vectors"

    def __init__(self, *args, **kwargs):
        BaseSignal.__init__(self, *args, **kwargs)

    #TODO: Fix plotting
    def plot(self):
        """Plot the diffraction vectors.
        """
        gvlist=[]
        for i in cali_peaks._iterate_signal():
            for j in np.arange(len(i[0])):
                gvlist.append(i[0][j])
        gvs = np.asarray(gvlist)

        import matplotlib.pyplot as plt
        plt.plot(gvs.T[1], gvs.T[0], 'ro')
        plt.axes().set_aspect('equal')
        plt.show()

    def get_magnitudes(self):
        """Calculate the magnitude of diffraction vectors.

        Returns
        -------
        magnitudes : BaseSignal
            Array

        """
        magnitudes = self.map(_calculate_norms, inplace=False)
        return magnitudes

    def get_magnitude_histogram(self, bins):
        """Obtain a histogram of gvector magnitudes.

        Parameters
        ----------

        bins :


        """
        gnorms = self.get_magnitudes()

        glist=[]
        for i in gnorms._iterate_signal():
            for j in np.arange(len(i[0])):
                glist.append(i[0][j])
        gs = np.asarray(glist)
        gsig = Signal1D(gs)
        ghis = gsig.get_histogram(bins=bins)
        ghis.axes_manager.signal_axes[0].name = 'g-vector magnitude'
        ghis.axes_manager.signal_axes[0].units = '$A^{-1}$'
        return ghis

    def get_unique_vectors(self):
        """Obtain a unique list of diffraction vectors.

        Returns
        -------
        unique_vectors : list
            Unique list of all diffraction vectors.
        """
        #Create empty list
        gvlist=[]
        for i in self._iterate_signal():
            for j in np.arange(len(i[0])):
                if np.asarray(i[0][j]) in np.asarray(gvlist):
                    pass
                else:
                    gvlist.append(i[0][j])
        gvs = np.asarray(gvlist)
        return gvs

    def get_vdf_images(self,
                       electron_diffraction,
                       radius,
                       unique_vectors=None):
        """Obtain the intensity scattered to each diffraction vector at each
        navigation position in an ElectronDiffraction Signal by summation in a
        circular window of specified radius.

        Parameters
        ----------
        unique_vectors : list (optional)
            Unique list of diffracting vectors if pre-calculated. If None the
            unique vectors in self are determined and used.

        electron_diffraction : ElectronDiffraction
            ElectronDiffraction signal from which to extract the reflection
            intensities.

        radius : float
            Radius of the integration window summed over in reciprocal angstroms.

        Returns
        -------
        vdfs : Signal2D
            Signal containing virtual dark field images for all unique g-vectors.
        """
        if unique_vectors==None:
            unique_vectors = self.get_unique_vectors()
        else:
            unique_vectors = unique_vectors

        vdfs = []
        for v in unique_vectors:
            disk = roi.CircleROI(cx=v[1], cy=v[0], r=radius, r_inner=0)
            vdf = disk(electron_diffraction,
                       axes=electron_diffraction.axes_manager.signal_axes)
            vdfs.append(vdf.sum((2,3)).as_signal2D((0,1)).data)
        return Signal2D(np.asarray(vdfs))

    def get_gvector_indexation(self,
                               calculated_peaks,
                               magnitude_threshold,
                               angular_threshold=None):
        """Index diffraction vectors based on the magnitude of individual
        vectors and optionally the angles between pairs of vectors.

        Parameters
        ----------

        calculated_peaks : array
            Structured array containing the theoretical diffraction vector
            magnitudes and angles between vectors.

        magnitude_threshold : Float
            Maximum deviation in diffraction vector magnitude from the
            theoretical value for an indexation to be considered possible.

        angular_threshold : float
            Maximum deviation in the measured angle between vector
        Returns
        -------

        gindex : array
            Structured array containing possible indexations
            consistent with the data.

        """
        #TODO: Specify threshold as a fraction of the g-vector magnitude.
        arr_shape = (self.axes_manager._navigation_shape_in_array
                     if self.axes_manager.navigation_size > 0
                     else [1, ])
        gindex = np.zeros(arr_shape, dtype=object)

        for i in self.axes_manager:
            it = (i[1], i[0])
            res = []
            for j in np.arange(len(glengths[it])):
                peak_diff = (calc_peaks.T[1] - glengths[it][j]) * (calc_peaks.T[1] - glengths[it][j])
                res.append((calc_peaks[np.where(peak_diff < magnitude_threshold)],
                            peak_diff[np.where(peak_diff < magnitude_threshold)]))
            gindex[it] = res

        if angular_threshold==None:
            pass
        else:
            pass

        return gindex

    def get_zone_axis_indexation(self):
        """Determine the zone axis consistent with the majority of indexed
        diffraction vectors.

        Parameters
        ----------

        Returns
        -------

        """
