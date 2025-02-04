

import cmasher as cmr
import numpy as np
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
from synthesizer.grid import Grid
from synthesizer import line_ratios
from synthesizer.line import get_line_label

# set style
plt.style.use('../../matplotlibrc.txt')

grid_dir = '/Users/sw376/Dropbox/Research/data/synthesizer/grids/test_suite/'
incident_grid = 'bpass-2.2.1-bin_chabrier03-0.1,300.0-ages:6.,7.,8.'
default_model = 'c23.01-sps'

variable_models = [
    ('ionisation_parameter', 'cmr.cosmic', 'U'),
    ('hydrogen_density', 'cmr.ember', 'n_{H}/cm^{-3}'),
    ('depletion_scale', 'cmr.wildfire', 'F_{\star}'),
    ('alpha', 'cmr.horizon', r'[\alpha/Fe]'),
    ]


# default grid
dgrid = Grid(f'{incident_grid}_cloudy-{default_model}-default', grid_dir=grid_dir)

# define ratios, diagrams, and lines to plot
diagrams = ['BPT-NII', 'OHNO']
diagrams = ['BPT-NII']
ratios = ['R3', 'R2', 'R23', 'S2', "O32", "Ne3O2"]
line_names = [line_ratios.Hb, line_ratios.Ha, line_ratios.O3, line_ratios.O2]

line_line_styles = [':', '-.', '--', '-']
ia = 0
metallicity_limits = [-4.99, -1.5]


for variable_model, cmap_name, parameter_label in variable_models:

    # define sub-cmap to ignore black and white
    cmap = cmr.get_sub_cmap(cmap_name, 0.1, 0.9)

    # open grid
    grid = Grid(f'{incident_grid}_cloudy-{default_model}-{variable_model}', grid_dir=grid_dir)

    # get variable parameter name
    variable_parameter_name = list(set(grid.axes) - {'log10age', 'metallicity'})[0]
    print(variable_parameter_name)

    # get the variable parameter
    variable_parameter = getattr(grid, variable_parameter_name)
    print(variable_parameter)

    # get colours
    colours = cmr.take_cmap_colors(
        cmap_name,
        len(variable_parameter),
        cmap_range=(0.15, 0.85))

    # ------------------------------------------------------------------------
    # line luminosity ratio diagram
    fig = plt.figure(figsize=(3.5, 2.))

    left = 0.15
    right = 0.9
    bottom = 0.025
    top = 0.85

    gs = fig.add_gridspec(
        2,
        2,
        hspace=0,
        wspace=0,
        left=left,
        right=right,
        bottom=bottom,
        top=top,)

    axes = gs.subplots()

    for line_name, ax in zip(line_names, axes.flatten()):

        for iv, (v, c) in enumerate(zip(variable_parameter, colours)):

            ratio = []

            for iz, metallicity in enumerate(grid.metallicity):

                dline = dgrid.get_line((ia, iz), line_name)
                line = grid.get_line((ia, iz, iv), line_name)

                ratio.append(np.log10(line.luminosity.value/dline.luminosity.value))

            ax.plot(
                np.log10(grid.metallicity), 
                ratio,
                lw=1,
                c=c,
                ls='-',
                zorder=2)

    for ax, line_name in zip(axes.flatten(), line_names):
        if isinstance(line_name, list):
            line_name = ','.join(line_name)
        line_label = rf'$\rm {get_line_label(line_name)}$'
        ax.text(-4.8, 0.7, line_label, fontsize=7)
        ax.axhline(0.0, c='k', alpha=0.2, lw=4)
        ax.set_xlim(metallicity_limits)
        ax.set_ylim([-0.99, 0.99])

    for ax in axes[1, :]:
        ax.set_xticklabels([])

    for ax in axes[0, :]:
        ax.tick_params(top=True, labeltop=True)

    for ax in axes[:, 1]:
        ax.yaxis.tick_right()
        # ax.set_yticklabels([])

    fig.supxlabel(r'$\rm log_{10}(Z)$', x=0.5*(left+right), y=0.94, fontsize=8)
    fig.supylabel(r'$\rm log_{10}(L/L_{default})$', x=0.025, y=0.45, fontsize=8)

    fig.savefig(f'figs/{variable_model}-luminosity_ratio.pdf')
    fig.clf()

    # ------------------------------------------------------------------------
    # ratios

    ncols = int(np.ceil(len(ratios)/2.))

    fig = plt.figure(figsize=(3.5, 3.))

    bottom = 0.125
    top = 0.95

    gs = fig.add_gridspec(
        ncols,
        2,
        hspace=0,
        wspace=0,
        left=left,
        right=right,
        bottom=bottom,
        top=top,)

    axes = gs.subplots()

    for ratio_id, ax in zip(ratios, axes.flatten()):

        for iv, (v, c) in enumerate(zip(variable_parameter, colours)):

            ratio = []

            for iz, metallicity in enumerate(grid.metallicity):
                grid_point = (ia, iz, iv)
                lines = grid.get_lines(grid_point)
                ratio.append(np.log10(lines.get_ratio(ratio_id)))

            ax.plot(
                np.log10(grid.metallicity), 
                ratio,
                lw=1,
                c=c,
                ls='-',
                zorder=2)

    for ax, ratio_id in zip(axes.flatten(), ratios):
        ax.set_xlim(metallicity_limits)
        ax.set_ylabel(ratio_id, fontsize=8)

    for ax in axes[:, 1]:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")
        # ax.set_yticklabels([])

    fig.supxlabel(r'$\log_{10}(Z)$', x=(left+right)/2., y=0.025, fontsize=8)

    fig.savefig(f'figs/{variable_model}-ratios.pdf')
    fig.clf()




    # ------------------------------------------------------------------------
    # diagrams

    for diagram_id in diagrams:

        fig = plt.figure(figsize=(3.5, 3.5))

        bottom = 0.15
        height = 0.8
        left = 0.15
        width = 0.8

        ax = fig.add_axes((left, bottom, width, height))

        if diagram_id == 'BPT-NII':
            # plot Kewley and Kauffmann lines if BPT
            for f, ls, limit, label in zip([line_ratios.get_bpt_kewley01, line_ratios.get_bpt_kauffman03],
                                        ['-', '--'],
                                        [0.47, 0.05],
                                        ['Kewley+2001', 'Kauffman+2003']):
                log10x = np.arange(-5., limit, 0.01)
                ax.plot(10**log10x, 10**f(log10x), ls=ls, lw=1, c='k', alpha=0.3, label=label)

        # plot default line diagram
        x = []
        y = []

        for iz, metallicity in enumerate(grid.metallicity):

            grid_point = (ia, iz)
            lines = dgrid.get_lines(grid_point)
            x_, y_ = lines.get_diagram(diagram_id)

            x.append(x_)
            y.append(y_)

        ax.plot(x, y, lw=3, c='k', alpha=0.2, zorder=1)

        # plot other models
        for iv, (v, c) in enumerate(zip(variable_parameter, colours)):

            x = []
            y = []

            for iz, metallicity in enumerate(grid.metallicity):

                grid_point = (ia, iz, iv)
                lines = grid.get_lines(grid_point)
                x_, y_ = lines.get_diagram(diagram_id)
                x.append(x_)
                y.append(y_)
                ax.scatter(x_, y_,s=5,c=c,marker='o')

            label = rf'$\rm {parameter_label}={v}$'

            ax.plot(x, y, ls='-', c=c, alpha=1.0, zorder=1, lw=1, label=label)


        # constant metallicity
        for iz, metallicity in enumerate(grid.metallicity):
        
            x = []
            y = []

            for iv, (v, c) in enumerate(zip(variable_parameter, colours)):

                grid_point = (ia, iz, iv)
                lines = grid.get_lines(grid_point)
                x_, y_ = lines.get_diagram(diagram_id)
                x.append(x_)
                y.append(y_)
                
            ax.plot(x, y, ls='-', c='k', alpha=0.1, zorder=1, lw=1)

        ax.legend(fontsize=6, labelspacing=0.05)

        ax.set_xlim([0.00001, 40])
        ax.set_ylim([0.001, 40])
        ax.set_xscale('log')
        ax.set_yscale('log')

        xlabel, ylabel = lines.get_diagram_labels(diagram_id)

        ax.set_xlabel(rf'$\rm {xlabel}$')
        ax.set_ylabel(rf'$\rm {ylabel}$')

        fig.savefig(f'figs/{variable_model}-{diagram_id}.pdf')
        fig.clf()