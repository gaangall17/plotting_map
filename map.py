from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import CARTODBPOSITRON, get_provider, OSM, STAMEN_TERRAIN_RETINA
from bokeh.models import ColumnDataSource, Grid, LinearAxis, Plot, Text
from pyproj import Transformer
import numpy as np
import pandas as pd

output_file("map.html")

tile_provider = get_provider(OSM)

INIT_LONG = -80.5
FINAL_LONG = -79.85
INIT_LAT = -2.30
FINAL_LAT = -2.00

WINDOW_PADDING = 5000

longlat_to_mercator = Transformer.from_crs('epsg:4326','epsg:3857', always_xy=True)

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
    locations = locations[['id','name','lat','long']]
    locations = locations.dropna(subset = ['lat'])
    locations = locations.set_index('id')
    text = []
    x = []
    y = []
    for index, row in locations.iterrows():
        if type(row[2]) == float and not(row[2] is None):
            text.append(index)
            xi, yi = longlat_to_mercator.transform(row[2], row[1])
            x.append(xi)
            y.append(yi)
    return text, x, y


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
    links = links[['id','equip1_slave_id','equip2_master_id','link_protocol','link_type']]
    links = links.dropna(subset = ['equip1_slave_id','equip2_master_id','link_type'])

    type = []
    x1 = []
    y1 = []
    x2 = []
    y2 = []
    for index, row in links.iterrows():
        if df[df['id']==row[1]]['long'].values.any() and df[df['id']==row[2]]['long'].values.any():
            type.append(row[4])

            xi, yi = longlat_to_mercator.transform(df[df['id']==row[1]]['long'].values, df[df['id']==row[1]]['lat'].values)
            x1.append(xi)
            y1.append(yi)

            xi, yi = longlat_to_mercator.transform(df[df['id']==row[2]]['long'].values, df[df['id']==row[2]]['lat'].values)
            x2.append(xi)
            y2.append(yi)

    return type, x1, y1, x2, y2


def run():
    
    text, x, y = get_locations('./data/locations.csv')

    type, x1, x2, y1, y2 = get_links('./data/locations.csv','./data/assets.csv','./data/links.csv')

    x_range, y_range = get_square_window(x, y)

    source = ColumnDataSource(dict(x=x, y=y, text=text))
    glyph = Text(x="x", y="y", text="text", angle=0, text_color="black", text_font_size='10px')

    p = figure(x_range=x_range, y_range=y_range, x_axis_type="mercator", y_axis_type="mercator", plot_width=1200, plot_height=600)
    p.add_tile(tile_provider)
    p.circle(x=x, y=y, size=15, color='blue')
    p.add_glyph(source, glyph)

    x_circle = []
    y_circle = []

    for i in range(len(type)):

        if 'radio' in type[i]:
            p.line([x1[i], y1[i]],[x2[i], y2[i]], color='black')
        else:
            x_circle.append(x1[i])
            y_circle.append(y1[i])
    
    p.circle(x=x_circle, y=y_circle, size=20, alpha=0.5, color='orange')
    show(p)


if __name__ == '__main__':
    run()
