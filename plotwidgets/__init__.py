import sys
import ipywidgets
from IPython.display import display 
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import inspect
import pandas
from collections import defaultdict
from functools import partial
import IPython.display

GRAPHICS = [
    sns.scatterplot,
    sns.relplot,
    sns.lineplot,
    sns.displot,
    sns.histplot,
    sns.kdeplot,
    sns.ecdfplot,
    sns.rugplot,
    sns.catplot,
    sns.stripplot,
    sns.swarmplot,
    sns.boxplot,
    sns.violinplot,
    sns.boxenplot,
    sns.pointplot,
    sns.barplot,
    sns.countplot,
    sns.lmplot,
    sns.regplot,
    sns.residplot,
    sns.heatmap,
    sns.clustermap,
    sns.jointplot,
]

def seaborn(data: pandas.DataFrame, plot: str | None, graphics: list | None, **kwargs: int | str | float) -> IPython.display.DisplayHandle:
    """
    This function is a wrapper for seaborn plots. It creates a set of dropdowns 
    for the most common parameters in seaborn plots.

    Parameters
    ----------
    data :
        The data to be plotted. A pandas.DataFrame.
    plot :
        The seaborn plot to be used. Default is `'scatterplot'`.
    graphics :
        A list of seaborn plotting functions to be used. Default is a list of common seaborn plotting functions.
    **kwargs
        Extra arguments passed to seaborn plotting function, such as `x`, `y`, `hue`, `row`, `col`, `palette`, `style`.
        See the [seaborn documentation](https://seaborn.pydata.org/) for all possible arguments.
        list of all possible arguments.

    Returns
    -------
    :
        The display of two ipywidgets objects: an HBox with the dropdowns and a seaborn plot.

    Examples
    --------    
    This code will display a scatter plot of `flipper_length_mm` against `body_mass_g` with 
    dropdown menus for `x`, `y`, and `hue` variables. Selecting form the dropdowns will update the plot.

    ```python
    import seaborn as sns
    import plotwidgets as pw
    data = sns.load_dataset('penguins')
    pw.seaborn(data, x='flipper_length_mm', y='body_mass_g', hue='species')
    ```
    """

    graphics = GRAPHICS

    sns.set_style('darkgrid')
    sns.set_palette('colorblind')

    kwargs = defaultdict(None, kwargs)
    if 'palette' in kwargs:
        sns.set_palette(kwargs['palette'])        
        del kwargs['palette']
    if 'style' in kwargs:
        sns.set_style(kwargs['style'])
        del kwargs['style']
    if 'graphics' in kwargs:
        graphics = kwargs['graphics']
        del kwargs['graphics']

 
    def plot(**dropdowns):

        _kwargs = kwargs.copy()
        if 'plot' in _kwargs:
            del _kwargs['plot']
        _kwargs.update(dropdowns)

        if 'plot' in _kwargs:
            selected_plot = _kwargs['plot']
            del _kwargs['plot']
        else:
            selected_plot = graphics[0]

        plt.close('all')

        # figsize = (6.5,4.5)
        if 'figsize' in _kwargs:
            figsize = _kwargs['figsize']
            del _kwargs['figsize']
        else:            
            figsize = matplotlib.rcParams['figure.figsize']

        try:
            # graphic_params = inspect.signature(selected_plot).parameters
            # if any(x in graphic_params for x in ['row', 'col']):
            if any(x in _kwargs for x in ['row', 'col']):
                if 'height' not in _kwargs:
                    _kwargs['height'] = figsize[1]*0.6
            selected_plot(data, **_kwargs)
        except NotImplementedError as e:
            print(e, file=sys.stderr)
            plt.close('all')            
            return
        except TypeError as e:
            print(f"{str(e).split(',')[0]}. That does not compatible with {selected_plot.__name__}", file=sys.stderr)
            print(e, file=sys.stderr)
            plt.close('all')            
            return
            # raise e
        # plt.title(f'{selected_plot.__name__.capitalize()} of {_kwargs['y']} against {_kwargs['x']}')
        plt.show()


    # TODO: filter graphics based on kwargs so only compatible graphics are shown

    [sns.relplot, sns.displot, sns.catplot, sns.displot]

    categorical_col_names = data.columns[(data.map(type) == str).all(0)].to_list()

    possible_graphics = []
    for g in graphics:
        sign = set(inspect.signature(g).parameters.keys()).union(set(['plot', 'palette', 'style', 'graphics']))
        param = set(kwargs.keys())
        # print(param, sign)
        if param.issubset(sign):
            possible_graphics.append(g)
    graphics = possible_graphics


    dropdowns = defaultdict(None)
    plot_options = [(g.__name__, g) for g in graphics]
    if 'plot' in kwargs:
        names, funs = zip(*plot_options)
        i = names.index(kwargs['plot'])
        plot_options = plot_options[i:i+1] + plot_options[:i] + plot_options[i+1:] 
    drop_down_plot = ipywidgets.Dropdown(options=plot_options, description='Plot:', disabled=False)
    dropdowns['plot'] = drop_down_plot

    for var in ['x', 'y', 'hue', 'row', 'col']:
        if var in kwargs:
            options = data.columns.to_list()
            if var in ['row', 'col']:
                options = data.columns[(data.map(type) == str).all(0)]
            drop_down = ipywidgets.Dropdown(options=options, value=kwargs[var], description=f'{var.capitalize()} variable:', disabled=False)
            dropdowns[var] = drop_down

    # if 'x' in kwargs:
    #     x_options = data.columns.to_list()
    #     drop_down_x = ipywidgets.Dropdown(options=x_options, value=kwargs['x'], description='X variable:', disabled=False)
    #     dropdowns['x'] = drop_down_x

    # if 'y' in kwargs:
    #     # if strings_as_cats:
    #     #     y_options = kwargs['data'].drop(categorical_col_names,axis=1).columns
    #     # else:
    #     #     y_options = kwargs['data'].columns.to_list()
    #     y_options = data.columns.to_list()
    #     drop_down_y = ipywidgets.Dropdown(options=y_options, value=kwargs['y'], description='Y variable:', disabled=False)
    #     dropdowns['y'] = drop_down_y

    # if 'hue' in kwargs:
    #     # if strings_as_cats:
    #     #     hue_options = kwargs['data'].columns[(df.map(type) == str).all(0)]
    #     # else:
    #     #     hue_options = kwargs['data'].columns.to_list()
    #     hue_options = data.columns.to_list()
    #     drop_down_hue= ipywidgets.Dropdown(options=hue_options, value=kwargs['hue'], description='Hue:', disabled=False)
    #     dropdowns['hue'] = drop_down_hue

    # if 'row' in kwargs:
    #     # row_options = data.columns.to_list()
    #     row_options = data.columns[(data.map(type) == str).all(0)]
    #     drop_down_row= ipywidgets.Dropdown(options=row_options, value=kwargs['row'], description='Row:', disabled=False)
    #     dropdowns['row'] = drop_down_row

    # if 'col' in kwargs:
    #     # col_options = data.columns.to_list()
    #     col_options = data.columns[(data.map(type) == str).all(0)]
    #     drop_down_col= ipywidgets.Dropdown(options=col_options, value=kwargs['col'], description='Col:', disabled=False)
    #     dropdowns['col'] = drop_down_col

    display(ipywidgets.HBox(list(dropdowns.values())),
            ipywidgets.interactive_output(plot, dropdowns))