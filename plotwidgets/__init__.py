import sys
from IPython.display import display, HTML, Markdown
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import inspect
import pandas
from pandas.api.types import is_numeric_dtype
from collections import defaultdict
import numpy as np
from math import sqrt

import ipywidgets as widgets
import IPython.display

import warnings

AXIS_LEVEL_GRAPHICS = [
    sns.scatterplot,
    sns.lineplot,
    sns.histplot,
    sns.kdeplot,
    # sns.ecdfplot,
    # sns.rugplot,
    sns.stripplot,
    sns.swarmplot,
    sns.boxplot,
    sns.violinplot,
    sns.boxenplot,
    sns.pointplot,
    sns.barplot,
    sns.countplot,
    # sns.residplot,
]
FIG_LEVEL_GRAPHICS = [
    sns.relplot,
    sns.displot,
    sns.catplot,
    sns.lmplot,
    sns.regplot,
    sns.jointplot,
]

AX2FIG = dict()
for kind in ['scatter', 'line']:
    AX2FIG[kind] = sns.relplot
for kind in ['hist', 'kde', 'ecdf']:
    AX2FIG[kind] = sns.displot
for kind in ['strip', 'swarm', 'box', 'violin', 'boxen', 'point', 'bar', 'count']:
    AX2FIG[kind] = sns.catplot
for kind in ['reg']:
    AX2FIG[kind] = sns.lmplot

OPTIONS = dict(
    max_figure_width=10, 
    max_figure_height=5,
    theme = dict(style='darkgrid', palette='viridis'),
    graphics=AXIS_LEVEL_GRAPHICS
    )


def set_options(**kwargs) -> None:
    """
    Calling `plotwidgets.seaborn with only the `data` positional argument will display dropdowns for all plot dimensions and include 
    all axis level seaborn graphics in the plot drowpdown. This function allows you limit the available plot dimensions and/or set their
    default values. It is also possible to set the plot theme by providing a dictionary with keyword arguments for seaborn.set_theme().

    Parameters
    ----------
    graphics : list
        A list of seaborn plotting functions to be used. Default is a list of common seaborn plotting functions.
    theme : dict
        Dictionary with keyword arguments for seaborn.set_theme().
    x : str
        Default value for x-axis dropdown.
    y : str
        Default value for y-axis dropdown.
    hue : str
        Default value for hue dropdown.
    col : str
        Default value for col dropdown.
    row : str
        Default value for row dropdown.

    Returns
    -------
    :
        None

    Examples
    --------    
    Limit the plot dimensions to 'x', 'y' and set the available graphics to 'scatterplot' and 'lineplot'.

    ```python
    import plotwidgets as pw
    pw.set_options(x=None, y=None, graphics=[sns.scatterplot, sns.lineplot])
    ```

    Do the same but set the default values for 'x' and 'y' to 'flipper_length_mm' and 'body_mass_g' respectively.
    
     ```python
    import plotwidgets as pw
    pw.set_options(x='flipper_length_mm', y='body_mass_g', graphics=[sns.scatterplot, sns.lineplot])
    ```

    Set the color palette to 'colorblind':

    ```python
    import plotwidgets as pw
    pw.set_options(theme={'palette': 'colorblind'})
    ```
    """    

    OPTIONS.update(kwargs)



# def seaborn(data: pandas.DataFrame, **kwargs) -> IPython.display.DisplayHandle:
def seaborn(data: pandas.DataFrame, x: str=None, y: str=None, hue: str=None, row: str=None, col: str=None) -> IPython.display.DisplayHandle:
    """
    This function is a wrapper for seaborn plots. It creates a set of dropdowns 
    for the most common parameters in seaborn plots.

    Parameters
    ----------
    data :
        The data to be plotted. A pandas.DataFrame.
    **kwargs
        Extra arguments passed to seaborn plotting functions.
        See the [seaborn documentation](https://seaborn.pydata.org/) for all possible arguments.
        list of all possible arguments.

    Returns
    -------
    :
        The display of two widgets objects: an HBox with the dropdowns and a seaborn plot.

    Examples
    --------    
    
    Import `plotwidgets` and `seaborn` to load the `penguins` example dataset:
    
    ```python
    import seaborn as sns
    data = sns.load_dataset('penguins')
    ```

    Show the plot widget with dropdowns for plot dimensions and for the plot graphic. Setting plot dimensions updates the available graphics in the "Plot" dropdown.
    dropdown menus for `x`, `y`, and `hue` variables. Selecting form the dropdowns will update the plot.

    ```python
    pw.seaborn(data)
    ```
    """

    kwargs = dict(x=x, y=y, hue=hue, row=row, col=col)
    plot_dimensions = ['x', 'y', 'hue', 'col', 'row']

    # use all dimensions as default, unless otherwise specified
    if all(kwargs[key] is None for key in plot_dimensions):
        for key in plot_dimensions:
            kwargs[key] = 'none'

    # remove dimensions with None values
    for key in plot_dimensions:
        if kwargs[key] is None:
            del kwargs[key]
    



    # # include preset options    
    # kwargs.update(OPTIONS)

    # set theme defaults if none provided
    if 'theme' in OPTIONS:
        sns.set_style(OPTIONS['theme'])
    # theme.setdefault('style', 'darkgrid')
    # theme.setdefault('palette', 'viridis')
    



    # # limit graphics
    # if 'graphics' in kwargs:
    #     used_graphics = kwargs['graphics']
    #     del kwargs['graphics']
    # else:
    #     used_graphics = AXIS_LEVEL_GRAPHICS

    # # FIXME: is this needed?
    # kwargs = defaultdict(None, kwargs)

    categorical_col_names = data.columns[(data.map(type) == str).all(0)].to_list()

    # dropdown controls
    dropdowns = defaultdict(None)

    # plot dropdown
    plot_options = [('none', 'none')]
    drop_down_plot = widgets.Dropdown(options=plot_options, description='Plot:', disabled=False)
    dropdowns['plot'] = drop_down_plot


    def _set_graphics_options(change):
        """
        Sets options in plot dropdown to fit the dropdown selections
        """
        _kwargs = kwargs.copy()
        for k, v in dropdowns.items():
            if v.value != 'none':
                _kwargs[k] = v.value

        options = []
        for g in OPTIONS['graphics']:

            not_plot_args = set(['plot', 'theme', 'graphics', 'row', 'col'])
            sign = set(inspect.signature(g).parameters.keys()).union(not_plot_args)
            param = set(k for k, v in _kwargs.items() if v != 'none' and v != None)
            if not param:
                continue
            if not param.issubset(sign):
                continue
            
            # more/better filters for graphics.....

            options.append(g)

        dropdowns['plot'].options = [('none', 'none')] + [(g.__name__, g) for g in options]





    # set initial plot dropdown options
    _set_graphics_options(None)

    # make dropdowns for plot dimensions
    for var in plot_dimensions:
        # only dims in kwargs
        if var in kwargs:
            # all variables
            options = ['none'] + data.columns.to_list()
            if var in ['row', 'col']:
                # only strings (categorical) values
                options = data.columns[(data.map(type) == str).any()].to_list()
                if not options:
                    # don't make dropdown if there are no string options
                    continue
                options = ['none'] + options
            # set default if any
            default = kwargs[var]
            if default is None:
                default = 'none'
            # make widget
            drop_down = widgets.Dropdown(options=options, value=default, 
                                         description=f'{var.capitalize()}:', disabled=False)
            dropdowns[var] = drop_down
            # make the dropdown trigger set_graphics_options when it changes
            dropdowns[var].observe(_set_graphics_options, names='value')

    # output widget for plot
    output = widgets.Output()

    # markdown widget for showing the plot code
    markdown_output = widgets.Output()

    # widget capturing any output from inside the _plot callback
    callback_output = widgets.Output(layout={'background-color': 'red'})

    @callback_output.capture(clear_output=True)    
    def _plot(btn):
        """
        Callback producing the plot
        """

        global markdown_html

        # get plotting parameters
        _kwargs = {}
        for k, v in kwargs.items():
            if v != 'none':
                _kwargs[k] = v
        for k, v in dropdowns.items():
            if v.value != 'none':
                _kwargs[k] = v.value

        # get plot and remove from _kwargs
        selected_plot = None
        if 'plot' in _kwargs and _kwargs['plot'] != 'none':
            selected_plot = _kwargs['plot']
            del _kwargs['plot']

        # FIXME: find a way to userspecify the discrete palette
        # set platte kwarg
        if 'hue' in _kwargs and _kwargs['hue']:
            if not is_numeric_dtype(data[_kwargs['hue']]):
                _kwargs['palette'] = "muted"
            else:
                _kwargs['palette'] = OPTIONS['theme']['palette']

        # close any plots in output
        plt.close('all') 

        # complain and return if no plot selected
        if selected_plot is None:
            print("No plot selected", file=sys.stderr)
            return callback_output

        # additional sensible parameters for some plots
        if selected_plot.__name__ == 'boxplot':
            added_kwargs = dict(gap=0.1, dodge=True)
            _kwargs.update(added_kwargs)

        # catch warnings like exceptions
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always") 

            # extra plot kwargs for figure level seaborn plots
            extra_kwargs = {}

            max_facet_height = 5
            min_facet_height = 2
            default_height = 5

            # find size of facets
            row_cats, col_cats = 1, 1
            if 'row' in _kwargs:
                row_cats = data.loc[~data[_kwargs['row']].isnull(), _kwargs['row']].unique().size
            if 'col' in _kwargs:
                col_cats = data.loc[~data[_kwargs['col']].isnull(), _kwargs['col']].unique().size

            possible_width = max(min_facet_height, min(max_facet_height, OPTIONS['max_figure_width'] / col_cats))
            possible_height = max(min_facet_height, min(max_facet_height, OPTIONS['max_figure_height'] / row_cats))
            if 'row' in _kwargs and 'col' in _kwargs:
                extra_kwargs['height'] = min(possible_width, possible_height)                
            elif 'row' in _kwargs:
                extra_kwargs['height'] = possible_height
            elif 'col' in _kwargs:


                tolerance = 0.01

                def find_facet_size(min_sq_size, max_sq_size):

                    sq_size = (min_sq_size + max_sq_size) / 2
                    if abs(sq_size - min_sq_size) < tolerance or abs(sq_size - max_sq_size) < tolerance:
                        return sq_size
                    sq_per_row = OPTIONS['max_figure_width'] // sq_size
                    sq_per_col = OPTIONS['max_figure_height'] // sq_size
                    sq_fitted = sq_per_row * sq_per_col
                    if sq_fitted < col_cats:
                        return find_facet_size(min_sq_size, sq_size)
                    else:
                        return find_facet_size(sq_size, max_sq_size)

                max_square_size = sqrt(OPTIONS['max_figure_height'] * OPTIONS['max_figure_width'] / col_cats)

                extra_kwargs['height'] = find_facet_size(0, max_square_size) - tolerance
                print(OPTIONS['max_figure_height'],  OPTIONS['max_figure_width'],  extra_kwargs['height'])
                extra_kwargs['col_wrap'] = int(OPTIONS['max_figure_width'] / extra_kwargs['height'])

            else:
                extra_kwargs['height'] = default_height

            # set kind for figure level plots
            kind = selected_plot.__name__.replace('plot', '')
            extra_kwargs['kind'] = kind 

            # if AX2FIG[kind].__name__ == 'relplot':
            #     extra_kwargs = dict(kind=kind, height=height, col_wrap=col_wrap)
            # if AX2FIG[kind].__name__ == 'catplot':
            #     extra_kwargs = dict(kind=kind, height=height)
            # if AX2FIG[kind].__name__ == 'lmplot':
            #     extra_kwargs = dict(kind=kind, height=height)
            # if AX2FIG[kind].__name__ == 'displot':
            #     extra_kwargs = dict(kind=kind, height=height)
                          
            figure_level_plot_function = AX2FIG[extra_kwargs['kind']]
            # extras.update(options_dict)
            # orig_fig_size = matplotlib.rcParams['figure.figsize']
            with output:
                # sns.set_theme(rc={"figure.figsize": figsize})
                g = figure_level_plot_function(data, **_kwargs, **extra_kwargs)
                g.set_titles(col_template="{col_name}", row_template="{row_name}")
                g.tight_layout()
                output.clear_output()
                plt.show()
            # matplotlib.rcParams['figure.figsize'] = orig_fig_size

            # # try:
            # if any(x in _kwargs for x in ['row', 'col']):

            #     # FIXME: implement as figure level graphics where there is a "kind" for the selected plot
            #     # If there is a "kind" for all axis plots, I could just do one facet if no row or col are specified...?



            #     # if 'height' not in _kwargs:
            #     #     _kwargs['height'] = figsize[1]*0.6
            #     facet_params = ['row', 'col', 'hue', 'palette']
            #     facet_kwargs = {k: _kwargs[k] for k in facet_params if k in _kwargs}
            #     plot_kwargs = {k: _kwargs[k] for k in _kwargs.keys() if k not in facet_params}
            #     plot_kwargs['legend'] = False

            #     facet_kwargs['palette'] = _kwargs['palette']
            #     with output:
            #         g = sns.FacetGrid(data, **facet_kwargs).map_dataframe(selected_plot, **plot_kwargs)
            #         h, l = g.axes.flat[0].get_legend_handles_labels()
            #         # print(h, l)
            #         # g.axes.flat[0].add_legend(h, l)

            #         if len(l) < 10:
            #             g.add_legend()

            #         # elif all(x in _kwargs and is_numeric_dtype(data[_kwargs[x]]) for x in ['x', 'y', 'hue']):
            #         #     norm = plt.Normalize(data[_kwargs['hue']].min(), data[_kwargs['hue']].max())
            #         #     cmap = sns.color_palette(theme['palette'], as_cmap=True)
            #         #     sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            #         #     ax = g.axes.flat[0]
            #         #     ax.figure.colorbar(sm, ax=ax)

            #         output.clear_output()
            #         plt.show()
            # else:
            #     with output:
            #         selected_plot(data, **_kwargs)
            #         output.clear_output()
            #         plt.show()


            # except NotImplementedError as e:
            #     print(e, file=sys.stderr)
            #     plt.close('all')            
            #     return
            # except TypeError as e:
            #     # print(f"{str(e).split(',')[0]}. That does not compatible with {selected_plot.__name__}", file=sys.stderr)
            #     # print(e, file=sys.stderr)
            #     # plt.close('all')            
            #     # return
            #     raise e
            # except Exception as e:
            #     raise e
            
            for warn in caught_warnings:
                if warn.category is not UserWarning:
                    print(warn.message)

            _kwargs.update(extra_kwargs)
            kw = ', '.join([f"{k}={repr(v)}" for k, v in _kwargs.items()])
            cmd = f'sns.{AX2FIG[kind].__name__}(data, {kw})'
            mdout = Markdown(f"""

<details>
<summary>Show code for plot</summary>
<br>
                             
```python
import seaborn as sns
sns.set_style({OPTIONS['theme']})                             
{cmd}
g.set_titles(col_template="{{col_name}}", row_template="{{row_name}}")
g.tight_layout()
```

<br>    
See the <a href=https://seaborn.pydata.org/generated/seaborn.{figure_level_plot_function.__name__}.html >documentation</a> 
for details and additional arguments to <code>sns.{figure_level_plot_function.__name__}</code>.

</details>

""")

            # markdown_html = widgets.HTML(mdout._repr_markdown_())
            with markdown_output:
                markdown_output.clear_output()
                display(mdout)

    button_layout = widgets.Layout(width='15em')
    button = widgets.Button(description='Show plot', layout=button_layout)
    button.on_click(_plot)
    button.add_class("button-spacing-class")
    display(HTML(
        "<style>.button-spacing-class {margin-left: 3em; margin-right: 2em;}</style>"
        ))
    
    dropdowns_layout = widgets.Layout(max_width='15em', height='auto',) #set width and height
    dropdowns_list = [widgets.Box([dropdowns[key]], layout=dropdowns_layout) for key in ['x', 'y', 'hue', 'row', 'col', 'plot'] if key in dropdowns]
    display(HTML(
        "<style> .widget-label { max-width: 3em !important; } </style>"
        ))

    dropdowns_layout = widgets.Layout(flex_flow='row wrap', margin_right= '5em')
    dropdowns_box = widgets.HBox(dropdowns_list, layout=dropdowns_layout)

    controls_layout = widgets.Layout(display='flex', flex_flow='row')
    controls = widgets.HBox([dropdowns_box, button], layout=controls_layout)

    # tab = widgets.Tab(children = [controls, options_text])
    # tab.set_title(0, 'Dimensions')
    # tab.set_title(1, 'Aesthetics')
    # display(tab)

    display(controls, output, markdown_output, callback_output)
    # display(tab, output, markdown_output, callback_output)

    return callback_output


