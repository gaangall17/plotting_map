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


def get_assets(path):
    locations = pd.read_csv(path)
    locations = locations[['id','name','lat','long']]
    locations = locations.set_index('id')
    print(locations.head(5))


def run():
    
    text, x, y = get_locations('./data/locations.csv')
    print(text)
    print(x)
    print(y)
    init_x, init_y = longlat_to_mercator.transform(INIT_LONG, INIT_LAT)
    final_x, final_y = longlat_to_mercator.transform(FINAL_LONG, FINAL_LAT)

    #text = ['E1', 'E2', 'E3', 'E4', 'E5']
    #N = len(text)

    #x = np.linspace(init_x, final_x, N)
    #y = np.linspace(init_y, final_y, N)

    x_range, y_range = get_square_window(x, y)

    source = ColumnDataSource(dict(x=x, y=y, text=text))
    glyph = Text(x="x", y="y", text="text", angle=0, text_color="black", text_font_size='10px')

    # range bounds supplied in web mercator coordinates
    p = figure(x_range=x_range, y_range=y_range, x_axis_type="mercator", y_axis_type="mercator", plot_width=1200, plot_height=600)
    p.add_tile(tile_provider)

    p.line(x[0:2],y[0:2], color='black')
    p.circle(x=x, y=y, size=15, color='blue')
    p.add_glyph(source, glyph)

    show(p)


if __name__ == '__main__':
    run()
