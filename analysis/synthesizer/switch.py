
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
default_model = 'c23.01-sps-default'

model_families = [
    
    # [('c23.01-fixed-depletion_model:None', 'no depletion'),
    #  ('c23.01-fixed-depletion_model:Gutkin2016', 'Gutkin+2016'),
    #  ('c23.01-fixed-depletion_model:ClassicCloudy', 'Classic Cloudy')],
    [('c23.01-sps-reference_abundance:Asplund2009', 'Asplund (2009) reference abundance pattern')],
    [('c23.01-sps-no_abundance_scalings', 'no element scaling')],
    
    [('c23.01-sps-constant_pressure', 'constant pressure')],
    # [('c23.01-sps-plane_parallel', 'plane parallel')],
]

model_families = {}

model_families['grains'] = [
    ('c23.01-sps-no_grains', 'no grains'),
    ('c23.01-sps-grains:ISM', 'ISM grains'),
    ('c23.01-sps-depletion_model:None', 'no depletion, no grains')
    ]

model_families['depletion'] = [
    ('c23.01-sps-depletion_model:CloudyClassic', 'Classic Cloudy depletion'),
    ('c23.01-sps-depletion_model:Gutkin2016', 'Gutkin+2016 depletion'),
    ('c23.01-sps-depletion_model:None', 'no depletion, no grains')
    ]

model_families['geometry'] = [
    ('c23.01-sps-planeparallel', 'plane parallel'),
    ('c23.01-sps-constant_pressure', 'constant pressure'),
    ]

model_families['abundance_pattern'] = [
    ('c23.01-sps-reference_abundance:Asplund2009', 'Asplund (2009) reference abundance pattern'),
    ('c23.01-sps-reference_abundance:Gutkin2016', 'Gutkin (2016) reference abundance pattern'),
    ('c23.01-sps-no_abundance_scalings', 'No N/O or C/O scaling with metallicity'),
    ]

family_names = ['grains', 'depletion', 'geometry', 'abundance_pattern']
# family_names = ['geometry']
# family_names = ['abundance_pattern']

# default grid
dgrid = Grid(f'{incident_grid}_cloudy-{default_model}', grid_dir=grid_dir)

diagrams = ['BPT-NII', 'OHNO']
diagrams = ['BPT-NII']
ratios = ['R3', 'R2', 'R23', 'S2', "O32", "Ne3O2"]
line_names = [line_ratios.Hb, line_ratios.Ha, line_ratios.O3, line_ratios.O2]

line_line_styles = [':', '-.', '--', '-']
ia = 0
metallicity_limits = [-4.99, -1.5]

# metallicity
metallicity_cmap = cmr.get_sub_cmap('cmr.torch', 0., 0.85)
metallicity_norm = Normalize(vmin=metallicity_limits[0], vmax=metallicity_limits[1])

model_line_styles = [':', '-.', '--', '-']

for family_name in family_names:
    
    model_family = model_families[family_name]

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

    for (model, label), ls in zip(model_family, model_line_styles):

        grid = Grid(f'{incident_grid}_cloudy-{model}', grid_dir=grid_dir)

        for line_name, ax in zip(line_names, axes.flatten()):

            ratio = []

            for iz, metallicity in enumerate(grid.metallicity):

                grid_point = (ia, iz)

                dline = dgrid.get_line(grid_point, line_name)
                line = grid.get_line(grid_point, line_name)

                ratio.append(np.log10(line.luminosity.value/dline.luminosity.value))

            ax.plot(
                np.log10(grid.metallicity), 
                ratio,
                lw=1,
                c='k',
                ls=ls,
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

    fig.savefig(f'figs/{family_name}-luminosity_ratio.pdf')
    fig.clf()

    # ------------------------------------------------------------------------
    # line ratios

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

        # default model
        ratio = []

        for iz, metallicity in enumerate(grid.metallicity):

            grid_point = dgrid.get_grid_point((0, metallicity))
            lines = grid.get_lines(grid_point)            
            ratio.append(np.log10(lines.get_ratio(ratio_id)))
        
        ax.plot(
            np.log10(grid.metallicity), 
            ratio,
            lw=2,
            c='k',
            ls='-',
            alpha=0.2,
            zorder=2)

        for (model, label), ls in zip(model_family, model_line_styles):

            grid = Grid(f'{incident_grid}_cloudy-{model}', grid_dir=grid_dir)

            ratio = []

            for iz, metallicity in enumerate(grid.metallicity):

                grid_point = grid.get_grid_point((0, metallicity))
                lines = grid.get_lines(grid_point)            
                ratio.append(np.log10(lines.get_ratio(ratio_id)))
            
            ax.plot(
                np.log10(grid.metallicity), 
                ratio,
                lw=1,
                c='k',
                ls=ls,
                zorder=2)

    for ax, ratio_id in zip(axes.flatten(), ratios):
        ax.set_xlim(metallicity_limits)
        ax.set_ylabel(ratio_id, fontsize=8)

    for ax in axes[:, 1]:
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")

    fig.supxlabel(r'$\log_{10}(Z)$', x=(left+right)/2., y=0.025, fontsize=8)

    fig.savefig(f'figs/{family_name}-ratios.pdf')
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

            # plot Kewley and Kauffmann lines 
            for f, ls, limit, label in zip(
                    [line_ratios.get_bpt_kewley01, line_ratios.get_bpt_kauffman03],
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
            # ax.scatter(x_, y_, marker='o', s=1, color=colour, zorder=2)

        ax.plot(x, y, lw=2, c='k', alpha=0.1, zorder=1, label = 'default')

        # plot other models
        for (model, label), ls in zip(model_family, model_line_styles):

            grid = Grid(f'{incident_grid}_cloudy-{model}', grid_dir=grid_dir)

            x = []
            y = []

            for iz, metallicity in enumerate(grid.metallicity):

                colour = metallicity_cmap(metallicity_norm(np.log10(metallicity)))
                grid_point = (ia, iz)
                lines = grid.get_lines(grid_point)
                x_, y_ = lines.get_diagram(diagram_id)

                x.append(x_)
                y.append(y_)
                ax.scatter(x_, y_, marker='o', s=5, color=colour, zorder=2)

            ax.plot(x, y, ls=ls, c='k', alpha=1.0, zorder=1, lw=1, label=label)

        ax.legend(fontsize=7, labelspacing=0.05)

        ax.set_xlim([0.00001, 40])
        ax.set_ylim([0.001, 40])
        ax.set_xscale('log')
        ax.set_yscale('log')

        xlabel, ylabel = lines.get_diagram_labels(diagram_id)

        ax.set_xlabel(rf'${xlabel}$')
        ax.set_ylabel(rf'${ylabel}$')

        figname = f'figs/{family_name}-{diagram_id}.pdf'
        print(figname)
        fig.savefig(figname)
        fig.clf()