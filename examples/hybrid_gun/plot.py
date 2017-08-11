import subprocess
import numpy as np
import matplotlib.pyplot as pl


def run(command):
    subprocess.run(command, shell=True, check=True)


def read_gpt_data():
    run('gdfa -o __py_beam_data.gdf output.gdf time avgx avgy avgz stdx stdy stdz stdBx stdBy stdBz')
    run('gdf2a -o __py_beam_data -w 16 __py_beam_data.gdf')
    data = {'time': [], 'avgx': [], 'avgy': [], 'avgz': [], 'stdx': [], 'stdy': [], 'stdz': [],
            'stdBx': [], 'stdBy': [], 'stdBz': []}
    with open('__py_beam_data', 'r') as f:
        f.readline()
        for line in f:
            foo = list(float(i) for i in line.split())
            if foo and foo[3] < 6:
                data['time'].append(foo[0])
                data['avgx'].append(foo[1])
                data['avgy'].append(foo[2])
                data['avgz'].append(foo[3])
                data['stdx'].append(foo[4])
                data['stdy'].append(foo[5])
                data['stdz'].append(foo[6])
                data['stdBx'].append(foo[7])
                data['stdBy'].append(foo[8])
                data['stdBz'].append(foo[9])
    run('rm __py_beam_data __py_beam_data.gdf')
    return data


def read_bmad_data():
    foo = []
    bar = []
    with open('__bmad_data', 'r') as f:
        line = f.readline()
        while '#' not in line:
            line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            foo.append(float(line.split()[1]) + 6)
            bar.append(float(line.split()[2]))
            line = f.readline()
    pl.plot(foo, bar, color="blue", marker='.')


def main():
    data = read_gpt_data()
    pl.plot(data['avgz'], data['stdx'], color='red', marker='.')
    read_bmad_data()
    pl.show()


main()
