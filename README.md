# PLOTTING MAP

Program to plot a communication map for IT or SCADA remote infraestructure using Bokeh library

Created by: Gabriel Gallardo - ga.gallardo95@gmail.com

## FEATURES

- Plot locations with different forms based on 3 states of connection: "linked", "not linked", and "working on"
- Reference different assets and communication links in the same location
- Plot radio links with lines
- Plot mobile, fiber and other external provider communications with a concentric circle
- Put colors on every link based on the communication Protocol
- Hover over locations or links to see more info

## INSTALLATION

- Create virtual environment "venv_plotting_map"
- pip install -r requirements.txt
- Run map.py
- You can look at the example and create a plot with it as reference
- To use your own data, create a "data" folder similar to "example" folder in the same level

## EXAMPLE IMAGES

![General](/img/plot1.png)

![Img 1](/img/plot2.png)

![Img 2](/img/plot3.png)

![Img 3](/img/plot4.png)

## LICENSE

MIT License