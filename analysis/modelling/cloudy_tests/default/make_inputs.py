
import numpy as np

# column density
values = np.arange(20., 22.5, 0.25)

for i, value in enumerate(values):
    i += 1
    lines_ = [
        r'table SED "incident.sed"',
        r'abundances "solar_GASS10.abn"',
        r'grains Orion',
        r'Q(H) = 49.22 # U=0.01, n_H = 100',
        r'radius -2.0 log parsecs',
        r'sphere',
        r'hden 2.0 log',
        r'constant density',
        r'iterate',
        f'stop column density {value}',
        r'stop temperature off',
        rf'save overview  "{i}.ovr" last',
        rf'save last abundances "{i}.abundances"',
        rf'save last continuum intrinsic "{i}.cont" units Angstroms no clobber', 
        rf'save line list column absolute last units angstroms "{i}.elin" "linelist.dat"', 
        rf'save line list emergent column absolute last units angstroms "{i}.eelin" "linelist.dat"', 
        rf'save last lines, array "{i}.lines" units Angstroms no clobber', 
    ]

    lines = [l+'\n' for l in lines_]

    with open(rf'{i}.in', 'w') as f:
        f.writelines(lines)

