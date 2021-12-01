#!/usr/bin/env python3
import argparse
import sys
import numpy as np
import math
import webbrowser
import requests
from os import path,remove



from stations import Station
from util_functions import *
from sources import Flux,Source,load_rfc_cat, get_up_sources


def print_sources(sources):
    print("{:>2} {:4} {:12} {:11} {:}".format('#', 'Cal?', 'Source name', 'Other name', 'Flux  Unresolved (at {}-band)'.format(rfcBand)))

    for i,source in enumerate(sources):
        if i > 9:
            break
        print("{:2} {:4} {:12} {:11} {:3.2f}  {:3.2f}".format(i, 'Y' if source.isCal else 'N', source.name, source.ivsname, source.flux[rfcBand].resolved, source.flux[rfcBand].unresolved))



#parse inputs
parser = argparse.ArgumentParser(description='Provide some options for sources to use as fringe finders.\nBased on RfC catalogue.')
parser.add_argument('timeStart', type=str, help="The start date/time of your experiment. Format ='DD/MM/YYYY HH:MM'")
parser.add_argument('duration', type=float, help="The duration of your experiment (in hours)")
parser.add_argument('-b', "--band", type=str, default='c', help="The band you are searching for, one of l, s, c, m, x, u, k, q.\nIf not specified will default to using C-band fluxes as priority.")
parser.add_argument('-e', "--min-el", type=int, default=20, help="The minimum elevation to consider a source being 'up'. Defaults to 20.")
parser.add_argument('-f', "--min-flux", type=float, default=1.0, help="The mimimum flux density of sources to consider. Defaults to 1.0 Jy")
parser.add_argument('stations',type=str, nargs='+', help="Space delimited list of stations")

args = parser.parse_args()

directory = path.dirname(path.realpath(__file__))
import wget
#need to get rfc catalogue if we don't have it
if not path.isfile(directory+"/rfc_2021c_cat.txt"):
    print("RFC VLBI Source Position Catalogue not found, downloading.\nThis might take a moment...")
    url = "http://astrogeo.org/vlbi/solutions/rfc_2021c/rfc_2021c_cat.txt"
    wget.download(url, out=directory)
    print("Done")

#rfc only has fluxes for bands, s, c, u, and k so pick the closest band to requested.
if args.band in ['l', 's']:
    rfcBand = 's'
elif args.band in ['c','m']:
    rfcBand = 'c'
elif args.band == 'x':
    rfcBand = 'x'
elif args.band == 'u':
    rfcBand = 'u'
elif args.band in ['k','q']:
    rfcBand = 'k'
else:
    #not a known band?
    print("Error band {} is unknown.".format(args.band))
    sys.exit(2)


#load station information for all stations.
stationList = Station.stations_from_file(directory+'/station_location.txt')
stations = [stationList[station.upper()] for station in args.stations]

obsTimes = get_obs_times(get_time(args.timeStart), args.duration)

sourceCat = load_rfc_cat(directory+"/rfc_2021c_cat.txt", rfcBand, args.min_flux)
sources = get_up_sources(stations, sourceCat, obsTimes, minEl=args.min_el, minFluxBand=rfcBand)

#ask which source to plot
while True:
    print()
    print_sources(sources)
    srcIndex = input("Please select the source to plot (0-9, q to quit): ")
    if srcIndex == 'q':
        break
    try: srcIndex = int(srcIndex)
    except ValueError:
        print("Must be an int (or q)!")
        continue

    if srcIndex in (list(range(10)) if len(sources) > 10 else list(range(len(sources)))):

        print("Astrogeo calibrator link, has source maps, radplots:")
        print(sources[srcIndex].get_astrogeo_link())
        #webbrowser.open(sourceCoordString, new=0, autoraise=True)

        links=sources[srcIndex].find_nmes()
        if len(links) > 0:
            print("The following NMEs have included this source:")
            for a,b in zip(links[::2], links[1::2]):
                print ("{:55} {:55}".format(a, b))
        else:
            print("No NME has included this source")



        #plot the elevations for the selected source
        sources[srcIndex].plot_elevation(stations, obsTimes)

    else:
        print("Not in range")



