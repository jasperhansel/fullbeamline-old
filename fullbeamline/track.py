import math
import os
import signal
import subprocess
from fullbeamline.cache import Cache
from fullbeamline.system_environment import system_environment
from fullbeamline.utilities import system


c = 299792458    # Speed of Light [m/s]
me = 510998.9461 # Electron Mass  [eV/c^2]


def read_parameters():
    """ Reads and returns a list of tuples containing the parameters of the simulation """
    with open('__fullbeamline/parameters', 'r') as f:
        file_contents = f.read()
    os.remove('__fullbeamline/parameters')
    parameters = []
    for line in file_contents.splitlines():
        parameters.append((line.split()[0], float(line.split()[2])))
    return tuple(parameters)


def callgpt(parameters):
    if system_environment.is_verbose:
        gpt_command = 'gpt -v -o output.gdf input GPTLICENSE=$GPTLICENSE'
    else:
        gpt_command = 'gpt -o output.gdf input GPTLICENSE=$GPTLICENSE'
    for var_value_tuple in parameters:
        gpt_command += ' {}={}'.format(*var_value_tuple)
    p = subprocess.Popen(gpt_command, shell=True, preexec_fn=os.setsid)
    try:
        p.wait(system_environment.timeout)
        if p.returncode != 0:
            return False
    except subprocess.TimeoutExpired:
        print('\033[31mtimeout\033[0m')
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        return False
    return True


def compute_statistics():
    system('gdfa -o __fullbeamline/statistics.gdf output.gdf position avgx avgy avgz avgBx avgBy avgBz avgG avgt avgp numpar Q')
    system('gdf2a -o __fullbeamline/statistics -w 16 __fullbeamline/statistics.gdf')
    with open('__fullbeamline/statistics', 'r') as f:
        contents = f.read().split()
    avgx = float(contents[13])
    avgy = float(contents[14])
    avgBx = float(contents[16])
    avgBy = float(contents[17])
    avgBz = float(contents[18])
    avgG = float(contents[19])
    reference_time = float(contents[20])
    reference_momentum = float(contents[21]) * c
    numpar = int(round(float(contents[22])))
    Q = float(contents[23])
    os.remove('__fullbeamline/statistics')
    os.remove('__fullbeamline/statistics.gdf')
    system('gdf2a -o __fullbeamline/output -w 16 output.gdf x Bx y By z Bz G t')
    with open('__fullbeamline/particles', 'w+') as new:
        new.write("0\n {avgx} {avgy} {avgpx} {avgpy} {avgpz} {qtot} {pref} {npart}\n".format(
            avgx=avgx,
            avgy=avgy,
            avgpx=avgBx * avgG * me / reference_momentum,
            avgpy=avgBy * avgG * me / reference_momentum,
            avgpz=(avgBz * avgG * me / reference_momentum) - 1,
            qtot=Q,
            pref=reference_momentum,
            npart=numpar
        ))
        with open('__fullbeamline/output', 'r') as old:
            while True:
                line = old.readline()
                assert line
                line = line.split()
                if line and line[0] == "position":
                    break
            old.readline()
            line = old.readline()
            particles = []
            while line.strip():
                x, y, z, Bx, By, Bz, G, t = (float(i) for i in line.split())
                new.write("{x} {Px} {y} {Py} {z} {Pz} {t}\n".format(
                    x = x,
                    Px = Bx * G * me / reference_momentum,
                    y = y,
                    Py = By * G * me / reference_momentum,
                    z =  -Bz * c * (t - reference_time),
                    Pz = (Bz * G * me / reference_momentum) - 1,
                    t = t - reference_time,
                ))
                line = old.readline()
    os.remove('__fullbeamline/output')


def convert_data(reference_time, reference_momentum, number_of_particles, total_charge):
    system('gdf2a -o __fullbeamline/output -w 16 output.gdf x Bx y By z Bz t')
    with open('__fullbeamline/particles', 'w+') as new:
        new.write("0\n {} {} {}\n".format(total_charge, reference_momentum, number_of_particles))
        with open('__fullbeamline/output', 'r') as old:
            while True:
                line = old.readline()
                assert line
                line = line.split()
                if line and line[0] == "position":
                    break
            old.readline()
            line = old.readline()
            particles = []
            while line.strip():
                x, y, z, Bx, By, Bz, t = (float(i) for i in line.split())
                new.write("{x} {Px} {y} {Py} {z} {Pz} {t}\n".format(
                    x = x,
                    Px = Bx / math.sqrt(1 - Bz ** 2) * me / reference_momentum,
                    y = y,
                    Py = By / math.sqrt(1 - Bz ** 2) * me / reference_momentum,
                    z =  -Bz * c * (t - reference_time),
                    Pz = (Bz / math.sqrt(1 - Bz ** 2) * me / reference_momentum) - 1,
                    t = t - reference_time,
                ))
                line = old.readline()
    os.remove('__fullbeamline/output')


def track():
    with Cache() as c:
        parameters = read_parameters()
        if not c.load(parameters):
            if not callgpt(parameters):
                with open('__fullbeamline/particles', 'w+') as f:
                    f.write('1\n')
                return
            compute_statistics()
            c.dump(parameters)
    return True
