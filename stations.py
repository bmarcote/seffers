import numpy as np
import astropy.units as u
import astropy.coordinates as coord
from astropy.io import ascii
#from sources import Source

class Station:

    def __init__(self, name, codename, location, sefds):
        """Initializes a station. The given name must be the name of the station that
        observes, with the typical 2-letter format used in the EVN (with exceptions).

        Inputs
        ------
        - name : str
            Name of the observer (the station that is going to observe).
        - codename : str
            A code for the name of the station. It can be the same as name.
        - location : EarthLocation
            Position of the observer on Earth.
        - sefds : dict
            SEFDs at different frequencies. Dict where keys are the wavelengths
            in cm. The values will be given in Jy. If a wavelngth is given, a correct
            SEFD is assumed (i.e. no empty or n/a values are expected to be found).
        """
        self.name = name
        self.code = codename
        self.location = location
        self.sefd = sefds


    def stations_from_file(filename):
        """The file must contain the following columns:
        name_observer code_observer X Y Z
        The header of this file should be "station code x y z", matching the previous fields

        Returns a dict with the observers. The keys are the code_observer.
        """
        file_with_stations = ascii.read(filename)
        # Getting the frequencies with SEFD values
        sefds = [acol for acol in file_with_stations.colnames if 'SEFD-' in acol]

        stations = {}
        for a_line in file_with_stations:
            a_loc = coord.EarthLocation(a_line['x']*u.m, a_line['y']*u.m, a_line['z']*u.m)
            stat_sefds = {}
            for a_sefd in sefds:
                if a_line[a_sefd] != -1:
                    stat_sefds[a_sefd.split('-')[1]] = a_line[a_sefd]

            stations[a_line['code']] = Station(a_line['station'], a_line['code'], a_loc,
                                               stat_sefds)

        return stations


    def source_elevation(self, source_coord, obs_times):
        """Returns the elevation of the source as seen by the Station during obs_times.

        Inputs
        ------
        - source_coord : astropy.coordinates
            Coordinates of the source to observe.
        - obs_times : astropy.time.Time
            Time to compute the elevation of the source (either single time or a list of times).

        Output
        ------
        - elevations : ndarray
            Elevation of the source at the given obs_times
        """
        source_altaz = source_coord.transform_to(coord.AltAz(obstime=obs_times,
                                                             location=self.location))
        return source_altaz.alt


    def is_source_visible(self, source_coord, obs_times, min_elevation):
        """Return if the source is visible for this station at the given time (with an
        elevation larger than the entered one).
        """
        elevations = self.source_elevation(source_coord, obs_times)
        return np.any(elevations >= min_elevation)



    def has_frequency(self, band):
        """Returns if the station can observe at the given band. This is
        expected to be given in wavelength (cm).
        """
        return band in self.sefd


    def get_sefd(self, band):
        """Return the SEFD of the station at the given band (given in cm).
        The SEFD value is given in Jy units.
        """
        return self.sefd[band]


