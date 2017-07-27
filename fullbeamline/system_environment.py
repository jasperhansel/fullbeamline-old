import os
import pathlib
import platform
import subprocess


warning = lambda message: print('\033[1mfullbeamline:\033[0m \033[33mwarning:\033[0m', message)


class SystemEnivronmentError(Exception):
    pass


class SystemEnvironment(object):

    def __init__(self):
        self.bash_init_file = '~/.bash_profile' if platform.system == 'Darwin' else '~/.bashrc'
        self.bmad_dir = pathlib.Path(os.getenv('DIST_BASE_DIR'))
        self.fullbeamline_dir = pathlib.Path(__file__).resolve().parent
        self.networking_activated = True
        self.detectGPT()
        self.detectBmad()
        self.detectOtherDependencies()


    def isBmadCompiled(self):
        try:
            subprocess.run('tao -noinit -noplot', shell=True, check=True, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            return False


    def detectGPT(self):
        try:
            result = subprocess.run('gpt -v', shell=True, check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise SystemEnivronmentError(
                'GPT not found. Please make sure GPT is installed and is invok'
                'able with the command \'gpt\'.'
            )
        if 'General Particle Tracer' not in result.stderr.decode():
            raise SystemEnivronmentError(
                'The command \'gpt\' invokes a program other than General Part'
                'icle Tracer.'
            )
        if os.getenv('GPTLICENSE') is None:
            raise SystemEnivronmentError(
                'The shell variable GPTLICENSE must be set to your GPT license'
                ' number. This can be done by running the command \'echo \'exp'
                'ort GPTLICENSE=X\' >> {}\' where X is your GPT license number'
                '.'.format(self.bash_init_file)
            )


    def detectBmad(self):
        if self.bmad_dir is None:
            raise SystemEnivronmentError(
                'Bmad not detected. Source code and install instructions can b'
                'e found at:\n https://www.classe.cornell.edu/~dcs/bmad/\nDon'
                '\'t forget to update your {} file as instructed.'
                .format(self_bash_init_file)
            )
        try:
            self.bmad_dir = self.bmad_dir.resolve()
        except FileNotFoundError as e:
            raise SystemEnivronmentError(
                'Shell variable \'DIST_BASE_DIR\' indicates Bmad directory is '
                'located at {}, yet nothing exists at that path. Please update'
                ' \'DIST_BASE_DIR\' in your {} file to the directory containing'
                ' Bmad, and then run \'source {}\''
                .format(self.bmad_dir, self.bash_init_file, self.bash_init_file)
            )


    def detectOtherDependencies(self):
        try:
            subprocess.run('curl --version', shell=True, check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            warning('cURL not found.')
            self.networking_activated = False
        try:
            import numpy
        except ImportError as e:
            raise SystemEnivronmentError('Unable to import numpy.')
        try:
            import matplotlib
        except ImportError as e:
            raise SystemEnivronmentError('Unable to import matplotlib.')
        try:
            import requests
        except ImportError as e:
            warning('unable to import requests')
            self.networking_activated = False


system_environment = SystemEnvironment()
