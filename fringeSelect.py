#!/usr/bin/env python3
import argparse
import numpy as np
from stations import Station
from util_functions import *

#parse inputs
parser = argparse.ArgumentParser(description='Provide some options for sources to use as fringe finders.\nBased on RfC catalogue.')
parser.add_argument('timeStart', type=str, help="The start date/time of your experiment. Format ='YYYY-MM-DD HH:MM:SS.S'")
parser.add_argument('duration', type=float, help="The duration of your experiment (in hours)")
parser.add_argument('-b', "--band", type=str, default="none", help="The band you are searching for, one of l, s, c, m, x, u, k, q")
parser.add_argument('stations',type=str, nargs='+', help="Space delimited list of stations")

args = parser.parse_args()

#load station information for all stations.
all_stations = Station.stations_from_file('./station_location.txt')

sourceCat = np.loadtxt('./rfc_2018c_cat.txt', comments='#', dtype={'names': ('cal', 'name', 'ivsname', 'raH', 'raM', 'raS', 'degH', 'degM',
                                                                             'degS', 'noObs', 'fluxSR', 'fluxSU', 'fluxCR', 'fluxCU',
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



