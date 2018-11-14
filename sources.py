class Flux:
    def __init__(self, resolvedFlux, unresolvedFlux):
        """Initialises a flux (contains unresolved and resolved flux)
        Inputs
        ------
        - resolvedFlux: the resolved flux of the source 
        - unresolvedFlux: the unresolved flux of the source 
        """
        self.resolved = resolvedFlux
        self.unresolved = unresolvedFlux
        assert isinstance(unresolvedFlux, float)
        assert isinstance(resolvedFlux, float)
    
class Source:

    def __init__(self, name, ivsname, coord, noObs, fluxes):
        """Initializes a source.

        Inputs
        ------
        - name: the J2000 name
        - ivsname: the ivsname
        - coord: astropy coord 
        - noObs: the number of times this source has been observed in the IVS cat (useful filter maybe)
        - fluxes: dict of fluxes with band as key names.
        """
        self.source = name
        self.ivsname = ivsname
        self.coord = coord
        self._noObs = noObs
        self.fluxes = fluxes

        
