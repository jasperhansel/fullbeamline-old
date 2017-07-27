from fullbeamline.system_environment import system_environment
import pathlib
import os
import shutil
import subprocess
import tempfile
import requests
import re


bmad_dir = system_environment.bmad_dir
fullbeamline_dir = system_environment.fullbeamline_dir
fortran_filenames = ('make_mat6_custom.f90', 'track1_beam_hook.f90', 'track1_custom.f90')


def build(build_type):
    if not system_environment.bmad_exists:
        print('\033[1mfullbeamline: \033[31merror: \033[0mBmad can\'t be compil'
              'ed because it is missing!')
    for filename in fortran_filenames:
        try:
            os.remove(str(bmad_dir / 'bmad' / 'custom' / filename))
        except FileNotFoundError:
            pass
        shutil.copy2(
            str(fullbeamline_dir / 'fortran' / filename),
            str(bmad_dir / 'bmad' / 'custom' / filename)
        )
    if build_type == 'debug':
        subprocess.run('cd {}; ./util/dist_build_debug'.format(bmad_dir), shell=True, check=True)
    elif build_type == 'production':
        subprocess.run('cd {}; ./util/dist_build_production'.format(bmad_dir), shell=True, check=True)
    else:
        raise ValueError("build type must be either 'debug' or 'production'")


def clean():
    if not system_environment.bmad_exists:
        print('\033[1mfullbeamline: \033[31merror: \033[0mBmad can\'t be cleane'
              'd because it is missing!')
    subprocess.run(str(bmad_dir / 'util' / 'dist_clean'), shell=True, check=True)


bmad_url = 'https://www.classe.cornell.edu/~cesrulib/downloads/tarballs'


info = lambda message: print('\033[1mfullbeamline:\033[0m \033[34minfo:\033[0m', message)

def update():
    info('deleting old files')
    try:
        shutil.rmtree(str(bmad_dir))
    except FileNotFoundError:
        pass
    info('obtaining distribution info')
    bmad_info = requests.get(bmad_url)
    bmad_dist_name = re.compile('bmad_dist_\d{4}_\d{4}').search(bmad_info.text).group()
    info('downloading bmad ({})'.format(bmad_dist_name))
    with tempfile.TemporaryDirectory() as temp_dir_name:
        bmad_tarball = pathlib.Path(temp_dir_name) / 'bmad.tgz'
        subprocess.run('curl {}/{}.tgz -o {}'.format(bmad_url, bmad_dist_name, bmad_tarball), shell=True, check=True)
        info('decompressing bmad')
        subprocess.run('tar -C {} -xzf {}'.format(temp_dir_name, bmad_tarball), shell=True, check=True)
        subprocess.run('mv {}/{} {}'.format(temp_dir_name, bmad_dist_name, bmad_dir), shell=True, check=True)
        subprocess.run('rm {}'.format(bmad_tarball), shell=True, check=True)
    info('done')
