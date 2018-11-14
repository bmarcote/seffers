
from os import path
import copy
import numpy as np
import datetime as dt

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import Slider, TextInput, Select, CheckboxGroup
from bokeh.plotting import figure, show

from bokeh.resources import CDN
from bokeh.embed import file_html



from astropy import coordinates as coord
from astropy.time import Time
from astropy import units as u
from astropy.io import ascii

from astroplan import Observer

from stations import Station



observation_types = ['EVN', 'e-EVN']

stations = {'EVN': ['EF', 'MC', 'ON', 'TR', 'JB2', 'WB', 'NT', 'SH', 'YS', 'HH', 'UR',
                    'SV', 'ZC', 'BD', 'IR', 'MH', 'SR', 'KM'],
            'e-EVN': ['EF', 'MC', 'ON', 'TR', 'JB2', 'WB', 'NT', 'SH', 'YS', 'HH', 'IR'],
            # 'Arecibo': ['AR'],
            'eMERLIN': ['CM', 'KN', 'TA', 'DE', 'DA'],
            'VLBA': ['VLBA-BR', 'VLBA-FD', 'GBT', 'VLBA-HN', 'VLBA-KP', 'VLBA-LA', 'VLBA-MK',
                    'VLBA-NL', 'VLBA-OV', 'PT', 'VLBA-SC', 'VLA'],
            'LBA': ['HO', 'PA', 'ATCA', 'CD', 'MO', 'TD', 'WW'],
            'KVN': ['KVN']}
# Include some more stations in some of the options
# Arecibo is tricky. Quite limited FoV!!!!!!!



# Widgets

# Lowest elevation to consider (would change color/marker in plots)
type_array = Select(title="Type observation", value="EVN", options=observation_types)
source = TextInput(title="Source coordinates (hh:mm:ss dd:mm:ss)", value="00:00:00 00:00:00")
epoch = TextInput(title="Starting UTC time (DD/MM/YYYY HH:MM)", value="01/01/2018 00:00")
duration = Slider(title="Duration of the observation (hours)", value=8.0, start=1.0, end=30.0, step=0.25)
elevation_limit = Slider(title="Lowest elevation (degrees)", value=10.0, start=0.0, end=50.0, step=5.0)
# Add checkboxes: include Ar, include eMERLIN, include VLBA, include LBA.
outstations = CheckboxGroup(labels=["eMERLIN", "VLBA", "LBA", "KVN"], active=[])



# useful functions

def get_coordinates(text_coord):
    """Given a string representing coordinates in the form hh:mm:ss dd:mm:ss
    if returns the astropy.coordinates from this object.
    """
    ra, dec = text_coord.strip().split(' ')
    ra = [float(i) for i in ra.split(':')]
    dec = [float(i) for i in dec.split(':')]
    return coord.SkyCoord('{:n}h{:n}m{}s {:n}d{:n}m{}s'.format(*ra, *dec))


def get_time(text_time):
    """Returns a datetime.datetime object representing the input text_time that
    should have the form DD/MM/YYYY HH:MM
    """
    # return Observer.datetime_to_astropy_time(dt.datetime.strptime(text_time, '%d/%m/%Y %H:%M'))
    the_time = dt.datetime.strptime(text_time, '%d/%m/%Y %H:%M')
    return Time(the_time.strftime('%Y-%m-%d %H:%M'))
    #date = [int(i) for i in date.split('/')]

def get_obs_times(start_time, duration, interval=0.2):
    """Returns the times of the observation from the starting to the end
    Duration and interval must be in hours, without units.
    """
    return start_time + np.arange(0.0, duration+interval/2., interval)*u.h



# Reading all stations
all_stations = Station.stations_from_file(path.dirname(__file__)+'/station_location.txt')

# Default parameters
source_coord = coord.SkyCoord('00h00m00s +00d00m00s')
times_obs = get_obs_times(get_time('01/01/2018 00:00'), duration.value)
selected_stations = copy.deepcopy(stations[type_array.value])
selected_all_stations = stations['EVN'] + stations['eMERLIN'] + stations['VLBA'] + stations['LBA']\
                + stations['KVN']



# Set up callbacks
def update_data(attrname, old, new):
    # get tge current slider values
    # print(outstations.active)
    # print(stations[type_array.value])
    selected_stations = copy.deepcopy(stations[type_array.value])
    # Include outstations if there are some active
    # print(selected_stations)
    for an_active in outstations.active:
        # print(an_active)
        for a_new_station in stations[outstations.labels[an_active]]:
            # print(a_new_station)
            selected_stations.append(a_new_station)

    # print(outstations.active)
    # print(selected_stations, '\n')

    # ADD LBA VLBA, eMERLIN,...
    times_obs = get_obs_times(get_time(epoch.value), duration.value)
    source_coord = get_coordinates(source.value)
    counter = 0
    # keys_to_remove = []
    # for a_key in data.keys():
    #     if a_key not in selected_stations:
    #         keys_to_remove.append(a_key)
    #
    # for a_key in keys_to_remove:
    #     dev_null = data.pop(a_key, None)

    # print(selected_stations)

    for a_station in selected_all_stations:
        if a_station in selected_stations:
            ys = all_stations[a_station].source_elevation(source_coord, times_obs)
        else:
            ys = (np.zeros_like(times_obs) - 90.)*u.deg

        # ys = all_stations[a_station].source_elevation(source_coord, times_obs)
        vs = np.zeros_like(ys) + counter*u.deg
        condition = np.where(ys >= elevation_limit.value*u.deg)
        data[a_station].data = dict(x=times_obs.datetime[condition], y=ys[condition],
                        v=vs[condition], station=[all_stations[a_station].station]*len(ys[condition]),
                        code=[all_stations[a_station].code]*len(ys[condition]))
        # Remove stations that are not anymore in the selected_stations

        counter -= 1



for a_w in [type_array, epoch, duration, source, elevation_limit]:
    a_w.on_change('value', update_data)

outstations.on_change('active', update_data)

# Set up layout with widgets and add to document
inputs = widgetbox(type_array, source, epoch, duration, elevation_limit, outstations)




data = {}
counter = 0
# for a_station in selected_stations:
for a_station in selected_all_stations:
    if a_station in selected_stations:
        ys = all_stations[a_station].source_elevation(source_coord, times_obs)
    else:
        ys = np.array([])
    # source is visible?
    # vs_cond = all_stations[a_station].is_source_visible(source_coord, times_obs, elevation_limit.value)
    vs = np.zeros_like(ys) + counter*u.deg
    condition = np.where(ys >= elevation_limit.value*u.deg)
    data[a_station] = ColumnDataSource(data=dict(x=times_obs.datetime[condition], y=ys[condition],
                        v=vs[condition], station=[all_stations[a_station].station]*len(ys[condition]),
                        code=[all_stations[a_station].code]*len(ys[condition])))
    # data[a_station] = ColumnDataSource(data=dict(x=times_obs.datetime, y=ys, #v=vs,
    #                     station=[all_stations[a_station].station]*len(ys)))
    counter -= 1


hover = HoverTool(tooltips=[("Station", "@station"), ("Elevation (deg)", "@y")])

########### Plots
# First plot: elevation versus time
golden_ratio = (np.sqrt(5) - 1.0)/2.0
plot1 = figure(plot_height=int(800*golden_ratio), plot_width=800, title='Antenna Elevation',
              x_axis_type="datetime", tools=[hover, "crosshair,pan,reset,wheel_zoom,save"])
              # x_axis_type="datetime", tools="crosshair,save")

for a_station in selected_all_stations:
    plot1.line('x', 'y', source=data[a_station], line_width=3, line_alpha=0.6)

plot1.xaxis.axis_label = "Time"
plot1.yaxis.axis_label = "Elevation (degrees)"
plot1.xgrid.visible = False
plot1.ygrid.visible = False


# Second plot: visibility versus time per station
plot2 = figure(plot_height=int(800*golden_ratio), plot_width=800, title='Source visibility',
            x_axis_type="datetime", tools=[hover, "crosshair,pan,reset,wheel_zoom,save"], 
            y_range=selected_all_stations[::-1])

for a_station in selected_all_stations:
    plot2.line(x='x', y='code', source=data[a_station], line_width=3, line_alpha=0.6)

plot2.xaxis.axis_label = "Time"
plot2.yaxis.axis_label = "Stations"
plot2.xgrid.visible = False
plot2.ygrid.visible = True




############## UV-plot
def get_uv_coordinates():
    pass





curdoc().add_root(row(inputs, column(plot1, plot2)))
# curdoc().add_root(row(inputs, plot1))
curdoc().title = "My Observation"


# output_server("source_visibility")
show()


