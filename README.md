## How to prompt chat gpt to yield proper responses

`
Compared to the initial non-interactive program, we have added lines 12-26. Line 13 creates a BinningIndexND that progressively maintains an index to all the numerical columns, allowing for quickly performing range queries over a large dataset. It is connected to the CSV module on line 15, with a slot hint restricting it to maintaining the index on two columns.

Line 17 creates a RangeQuery2D module that creates a table filtered by a 2D range query. The outputs of this module are connected to the Histogram2D module on lines 30-32 instead of the min/max quantiles and the table produced by the CSV table in the first example. The RangeQuery2D module outputs the current min/max ranges and the table filtered according to these ranges to the Histogram2D module, which gets visualized like in the first example. The RangeQuery2D module takes two variables var_min and var_max, declared line 19-20m to specify the desired min-max range that the user wants to see. The variables can be controlled by a Jupyter notebook range-query widget to pass the information from the notebook to the progressive program, as shown in the next listing.

import ipywidgets as widgets
import progressivis.core.aio as aio

# Yield control to the scheduler to start
await aio.sleep(1)

# Define the bounds for the range-slider widgets
bnds_min = PDict({col_x: bounds.left, col_y: bounds.bottom})
bnds_max = PDict({col_x: bounds.right, col_y: bounds.top})

# Assign an initial value to the min and max variables
await var_min.from_input(bnds_min)
await var_max.from_input(bnds_max);

long_slider = widgets.FloatRangeSlider(
    value=[bnds_min[col_x], bnds_max[col_x]],
    min=bnds_min[col_x],
    max=bnds_max[col_x],
    step=(bnds_max[col_x]-bnds_min[col_x])/10,
    description='Longitude:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='.1f',
)
lat_slider = widgets.FloatRangeSlider(
    value=[bnds_min[col_y], bnds_max[col_y]],
    min=bnds_min[col_y],
    max=bnds_max[col_y],
    step=(bnds_max[col_y]-bnds_min[col_y])/10,
    description='Latitude:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='.1f',
)
def observer(_):
    async def _coro():
        long_min, long_max = long_slider.value
        lat_min, lat_max = lat_slider.value
        await var_min.from_input({col_x: long_min, col_y: lat_min})
        await var_max.from_input({col_x: long_max, col_y: lat_max})
    aio.create_task(_coro())
long_slider.observe(observer, "value")
lat_slider.observe(observer, "value")
widgets.VBox([long_slider, lat_slider])
Lines 11 and 12 use the Module.from_input method to initialize the value of var_min and var_max to bnds_min and bnds_max respectively. Then, two range sliders are created on lines 14 and 26 to filter a range of values between the specified bounds of the visualization. The observer() function is attached as a callback of these two sliders to collect the slider values and send them to var_min and var_max on lines 42-43. Setting them in the callback will force the histogram to recompute with the new bounds and, in turn, trigger an update of the heatmap every time the sliders are moved.

Building a progressive visualization and making it interactive is conceptually easy with ProgressiVis, but it may require a lot of boilerplate code. To simplify the construction of complex loading, analysis, and visualization of progressive pipelines, we provide higher-level abstractions in Jupyter Lab notebooks. They are documented in the notebooks section.
`
- Give ChatGPT this text and ask it to generate the code for progressivis snippet. 
