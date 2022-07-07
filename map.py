from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import CARTODBPOSITRON, get_provider, OSM, STAMEN_TERRAIN_RETINA
from bokeh.models import ColumnDataSource
from pyproj import Transformer
import numpy as np
import pandas as pd

WINDOW_PADDING = 5000

TOOLTIPS = [
        ("Codigo", "@text"),
        ("Nombre", "@name"),
        ("Tipo", "@type")
    ]


#Protocol type dictionary, used to represent a different color for every protocol
DICT_COLOR = {
    'MODBUS SERIAL': 'cyan',
    '4-20': 'black',
    'DNP3': 'black',
    'DNP3 SERIAL': 'orange',
    'DNP3 TCP': 'red',
    'MODBUS TCP': 'green',
    'ETHERNET': 'blue'
}


#Connection status dictionary, used to represent the form of the location
DICT_STATUS_MARKER = {
    'linked': 'circle',
    'not linked': 'x',
    'working on': 'triangle'
}


#Object to transform from Long, Lat to X, Y
longlat_to_mercator = Transformer.from_crs('epsg:4326','epsg:3857', always_xy=True)


#Defining the coordenates for the initial plot view
def get_square_window(x, y):
    x_max = np.max(x)
    x_min = np.min(x)
    y_max = np.max(y)
    y_min = np.min(y)

    if x_max - x_min >= y_max - y_min:
        delta_x = 0 + WINDOW_PADDING
        delta_y = ((x_max - x_min) - (y_max - y_min))/2 + WINDOW_PADDING
    else:
        delta_x = ((y_max - y_min) - (x_max - x_min))/2 + WINDOW_PADDING
        delta_y = 0 + WINDOW_PADDING

    x_range = (x_min - delta_x, x_max + delta_x)
    y_range = (y_min - delta_y, y_max + delta_y)

    return x_range, y_range


def get_locations(path):
    locations = pd.read_csv(path)
    locations = locations[['id','name','lat','long','type_id','scada_status']]
    locations = locations.dropna(subset = ['lat'])
    locations = locations.set_index('id')
    text = []
    name = []
    type_location = []
    status = []
    x = []
    y = []
    lat = []
    long = []
    for index, row in locations.iterrows():
        if type(row[2]) == float and not(row[2] is None):
            text.append(index)
            name.append(row[0])
            type_location.append(row[3])
            status.append(row[4])
            lat.append(row[1])
            long.append(row[2])
            xi, yi = longlat_to_mercator.transform(row[2], row[1])
            x.append(xi)
            y.append(yi)
    
    #Create a Bokeh data source to plot the locations
    source_location = ColumnDataSource(dict(
        x=x, 
        y=y, 
        text=text, 
        name=name, 
        type=type_location,
        marker=[DICT_STATUS_MARKER[s] for s in status]
    ))

    return x, y, source_location


def get_links(path_locations, path_assets, path_links):
    locations = pd.read_csv(path_locations)
    locations = locations[['id','lat','long']]
    locations = locations.dropna(subset = ['lat'])
    locations = locations.set_index('id')

    assets = pd.read_csv(path_assets)
    assets = assets[['id','<location_id>']]
    assets = assets.dropna(subset = ['<location_id>'])
    assets = assets.set_index('<location_id>')

    df = pd.merge(locations, assets, left_index=True, right_index=True)

    links = pd.read_csv(path_links)
    links = links[['id','equip1_slave_id','equip2_master_id','link_protocol','link_type','equip1_slave_name','equip2_master_name']]
    links = links.dropna(subset = ['equip1_slave_id','equip2_master_id','link_type','link_protocol'])

    protocol_radio = []
    id_radio = []
    name_radio = []
    type_radio = []
    x1 = []
    y1 = []
    x2 = []
    y2 = []

    protocol_other = []
    id_other = []
    name_other = []
    type_other = []
    x = []
    y = []

    for index, row in links.iterrows():
        if df[df['id']==row[1]]['long'].values.any() and df[df['id']==row[2]]['long'].values.any():
            if 'radio' in row[4]:
                type_radio.append(row[4])
                protocol_radio.append(row[3])
                id_radio.append(row[0])
                name_radio.append("Enlace: " + row[5] + " -> " + row[6])
                xi, yi = longlat_to_mercator.transform(df[df['id']==row[1]]['long'].values, df[df['id']==row[1]]['lat'].values)
                x1.append(xi)
                y1.append(yi)

                xi, yi = longlat_to_mercator.transform(df[df['id']==row[2]]['long'].values, df[df['id']==row[2]]['lat'].values)
                x2.append(xi)
                y2.append(yi)
            else:
                type_other.append(row[4])
                protocol_other.append(row[3])
                id_other.append(row[0])
                name_other.append("Enlace: " + row[5])
                xi, yi = longlat_to_mercator.transform(df[df['id']==row[1]]['long'].values, df[df['id']==row[1]]['lat'].values)
                x.append(xi)
                y.append(yi)
            
    #Create a Bokeh data source to plot radio links
    source_radio_link = ColumnDataSource(dict(
        xs=[[x1[i][0], x2[i][0]] for i in range(len(x1))], 
        ys=[[y1[i][0], y2[i][0]] for i in range(len(y1))],
        text=id_radio,
        type=type_radio, 
        name=name_radio, 
        color=[DICT_COLOR[p] for p in protocol_radio]
    ))

    #Create a Bokeh data source to plot other communication links
    source_other_link = ColumnDataSource(dict(
        x=[x[i][0] for i in range(len(x))], 
        y=[y[i][0] for i in range(len(y))],
        text=id_other,
        type=type_other, 
        name=name_other, 
        color=[DICT_COLOR[p] for p in protocol_other]
    ))

    return source_radio_link, source_other_link


def run(folder_path):
    
    output_file(folder_path + "map.html")

    tile_provider = get_provider(CARTODBPOSITRON)

    x, y, source_location = get_locations(folder_path + 'locations.csv')

    source_radio_link, source_other_link = get_links(folder_path + 'locations.csv', 
                                                    folder_path + 'assets.csv',
                                                    folder_path + 'links.csv')

    x_range, y_range = get_square_window(x, y)

    plot = figure(x_range=x_range, y_range=y_range,
            x_axis_type="mercator", y_axis_type="mercator",
            plot_width=1200, plot_height=600,
            tooltips=TOOLTIPS)

    plot.add_tile(tile_provider)

    #Plotting radio links
    plot.multi_line(xs='xs', ys='ys', line_width=2, line_color='color', source=source_radio_link)

    #Plotting other communications
    plot.circle(x='x', y='y', size=20, alpha=0.5, color='color', source=source_other_link)

    #Plotting locations
    plot.scatter(x='x', y='y', size=10, color='blue', alpha=0.7, marker='marker', source=source_location)

    show(plot)


if __name__ == '__main__':
    print('--Plotting map--')
    mode = int(input('[1] Example or [2] Data: '))
    if mode == 1:
        print('Plotting example ...')
        run('./example/')
        print('Example plotted!')
    elif mode == 2:
        print('Plotting map with data ...')
        run('./data/')
        print('Map plotted!')
    else:
        print('--Ending program--')
