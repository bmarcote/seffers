#!/usr/bin/env python3
import argparse
import sys
import numpy as np
from astropy import coordinates as coord
from os import path,remove
import requests
from tqdm import tqdm
import math

from stations import Station
from util_functions import *
from sources import Flux,Source

#parse inputs
parser = argparse.ArgumentParser(description='Provide some options for sources to use as fringe finders.\nBased on RfC catalogue.')
parser.add_argument('timeStart', type=str, help="The start date/time of your experiment. Format ='DD/MM/YYYY HH:MM'")
parser.add_argument('duration', type=float, help="The duration of your experiment (in hours)")
parser.add_argument('-b', "--band", type=str, default='c', help="The band you are searching for, one of l, s, c, m, x, u, k, q.\nIf not specified will default to using C-band fluxes as priority.")
parser.add_argument('stations',type=str, nargs='+', help="Space delimited list of stations")

args = parser.parse_args()

#need to get rfc catalogue if we don't have it
if not path.isfile("./rfc_2018c_cat.txt"):
    print("RFC VLBI Source Position Catalogue not found, downloading.\nThis might take a moment...")
    url = "http://astrogeo.org/vlbi/solutions/rfc_2018c/rfc_2018c_cat.txt"
    r = requests.get(url, stream=True)
    # Total size in bytes.
    total_size = int(r.headers.get('content-length', 0));
    block_size = 1024
    wrote = 0
    with open('rfc_2018c_cat.txt', 'wb') as f:
            for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size//block_size) , unit='KB', unit_scale=True):
                wrote = wrote  + len(data)
                f.write(data)
    if total_size != 0 and wrote != total_size:
        print("ERROR, something went wrong with the download.")
        remove("./rm rfc_2018c_cat.txt")
        sys.exit(1)
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
stationList = Station.stations_from_file('./station_location.txt')

obsTimes = get_obs_times(get_time(args.timeStart), args.duration)

#loads the data initially from the rfc catalogue, note we have to take care of < in the fluxes. We ignore position error columns
sourceCat = np.loadtxt('./rfc_2018c_cat.txt',
                       comments='#',
                       dtype={'names': ('cal', 'name', 'ivsname', 'raH', 'raM', 'raS', 'decD', 'decM',
                                        'decS', 'noObs', 'fluxSR', 'fluxSU', 'fluxCR', 'fluxCU',
                                        'fluxXR', 'fluxXU', 'fluxUR', 'fluxUU', 'fluxKR', 'fluxKU'),
                              'formats': ('bool', '|S15', '|S15', 'int', 'int', 'float', 'int', 'int',
                                          'float', 'int', 'float', 'float', 'float', 'float', 'float',
                                          'float', 'float', 'float', 'float', 'float')},
                       usecols=(0,1,2,3,4,5,6,7,8,12,13,14,15,16,17,18,19,20,21,22),
                       converters={0: lambda cal: True if cal=='Y' else False,
                                   13: lambda f: 0.0 if '<' in str(f) else f,
                                   14: lambda f: 0.0 if '<' in str(f) else f,
                                   15: lambda f: 0.0 if '<' in str(f) else f,
                                   16: lambda f: 0.0 if '<' in str(f) else f,
                                   17: lambda f: 0.0 if '<' in str(f) else f,
                                   18: lambda f: 0.0 if '<' in str(f) else f,
                                   19: lambda f: 0.0 if '<' in str(f) else f,
                                   20: lambda f: 0.0 if '<' in str(f) else f,
                                   21: lambda f: 0.0 if '<' in str(f) else f,
                                   22: lambda f: 0.0 if '<' in str(f) else f})



sources=[]
for source in sourceCat:
    fluxes = {'s': Flux(source['fluxSR'], source['fluxSU']),
              'c': Flux(source['fluxCR'], source['fluxCU']),
              'u': Flux(source['fluxUR'], source['fluxUU']),
              'k': Flux(source['fluxKR'], source['fluxKU'])}
    #speed up hugely if we only care about bright sources:
    if fluxes[rfcBand].unresolved > 0.5:
        name = source['name'].decode()
        ivsname = source['ivsname'].decode()
        coords = coord.SkyCoord("{:02d}h{}m{}s {:+d}d{}m{}s".format(source['raH'], source['raM'], source['raS'], source['decD'], source['decM'], source['decS']))
        for station in args.stations:
            if len(stationList[station.upper()].is_source_visible(coords, obsTimes, 20)[0]) < 1:
                break
        else:
            #note this else applies to the loop, not the above if statement. i.e we only append sources up for all stations
            sources.append(Source(name, ivsname, coords, source['noObs'], fluxes))

def getRfcBandFlux(source):
    return source.flux[rfcBand].unresolved

sources.sort(key=getRfcBandFlux, reverse=True)
for i,source in enumerate(sources):
    if i > 10:
        break
    print("{:10}{:3.2f}".format(source.name, source.flux[rfcBand].unresolved))
