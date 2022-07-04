from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from bokeh.models import ColumnDataSource, Grid, LinearAxis, Plot, Text
import numpy as np

output_file("map.html")

tile_provider = get_provider(CARTODBPOSITRON)

text = ['E1', 'E2', 'E3', 'E4', 'E5']

N = len(text)
x = np.linspace(-1500000, 5500000, N)
y = np.linspace(-500000, 6500000, N)

source = ColumnDataSource(dict(x=x, y=y, text=text))
glyph = Text(x="x", y="y", text="text", angle=0, text_color="black")

# range bounds supplied in web mercator coordinates
p = figure(x_range=(-2000000, 6000000), y_range=(-1000000, 7000000),
           x_axis_type="mercator", y_axis_type="mercator")
p.add_tile(tile_provider)
p.line([x[0],x[1]],[y[0],y[1]], color='black')
p.circle(x=x, y=y, size=10, color='orange')
p.add_glyph(source, glyph)

show(p)