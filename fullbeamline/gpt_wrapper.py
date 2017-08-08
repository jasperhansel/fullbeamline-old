import math
import subprocess
import os
import sys
import pickle
import multiprocessing


c = 299792458    # Speed of Light [m/s]
me = 510998.9461 # Electron Mass  [eV/c^2]


def system(command):
    subprocess.run(command, shell=True, check=True)


def read_parameters():
    with open('__parameters', 'r') as f:
        file_contents = f.read()
    os.remove('__parameters')
    parameters = {}
    for line in file_contents.splitlines():
        parameters[line.split()[0]] = float(line.split()[2])
    return parameters


def run_gpt(parameters):
    gpt_command = 'gpt -o output.gdf input.in GPTLICENSE=$GPTLICENSE'
    for variable, value in parameters.items():
        gpt_command += ' {}={}'.format(variable, value)
    def runcmd():
        os.system(gpt_command)
    p = multiprocessing.Process(target=runcmd)
    p.start()
    max_gpt_run_time = int(os.environ['FULLBEAMLINE_GPT_TIMEOUT_CAP'])
    p.join(max_gpt_run_time)
    if p.is_alive():
        print("\033[31mtimeout\033[0m")
        p.terminate()
        p.join()
        return False
    return True


def compute_statistics():
    system('gdfa -o __statistics.gdf output.gdf position avgt avgp numpar Q')
    system('gdf2a -o __statistics -w 16 __statistics.gdf')
    with open('__statistics', 'r') as f:
        contents = f.read().split()
    reference_time = float(contents[6])
    reference_momentum = float(contents[7]) * c
    number_of_particles = int(round(float(contents[8])))
    total_charge = float(contents[9])
    os.remove('__statistics.gdf')
    os.remove('__statistics')
    return reference_time, reference_momentum, number_of_particles, total_charge


def convert_data(reference_time, reference_momentum, number_of_particles, total_charge):
    system('gdf2a -o __output -w 16 output.gdf x Bx y By z Bz t')
    with open('__particles', 'w+') as new:
        new.write("0\n {} {} {}\n".format(total_charge, reference_momentum, number_of_particles))
        with open('__output', 'r') as old:
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
    os.remove('__output')


def callgpt():
    parameters = read_parameters()
    if os.path.isfile('__fullbeamline_cache') and os.path.isfile('__particles'):
        with open('__fullbeamline_cache', 'rb') as f:
            old_parameters = pickle.load(f)
        if (parameters == old_parameters):
            print('--> using cached GPT data')
            return
    print('--> calling gpt: ', end='')
    sys.stdout.flush()
    if not run_gpt(parameters):
        with open('__particles', 'w+') as f:
            f.write('1\n')
        with open('__fullbeamline_cache', 'wb+') as f:
            pickle.dump(parameters, f)
        return
    reference_time, reference_momentum, number_of_particles, total_charge = compute_statistics()
    convert_data(reference_time, reference_momentum, number_of_particles, total_charge)
    with open('__fullbeamline_cache', 'wb+') as f:
        pickle.dump(parameters, f)
    print('\033[32mok\033[0m')
