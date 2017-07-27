import os
import sys
import pathlib
import platform
import subprocess


class SystemEnivronmentError(Exception):
    pass


class SystemEnvironment(object):

    def __init__(self):
        self.bash_file = '~/.bash_profile' if platform.system == 'Darwin' else '~/.bashrc'
        self.fullbeamline_dir = pathlib.Path(__file__).resolve().parent
        self.detectGPT()
        self.detectBmad()
        self.detectCURL()

    def detectGPT(self):
        try:
            result = subprocess.run('gpt -v', shell=True, check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print('\033[1mfullbeamline: \033[31merror: \033[0mGPT not found. pl'
                  'ease make sure GPT is installed and is invokable with the co'
                  'mmand \'gpt\'')
            sys.exit(1)
        if 'General Particle Tracer' not in result.stderr.decode():
            print('\033[1mfullbeamline: \033[31merror: \033[0mThe command \'gpt'
                  '\' invokes a program other than General Particle Tracer.')
            sys.exit(1)
        if os.getenv('GPTLICENSE') is None:
            print('\033[1mfullbeamline: \033[31merror: \033[0mThe bash variable'
                  ' GPTLICENSE is not set to your GPT license number. Please ad'
                  'd \'export GPTLICENSE=X\' to your {} file where X is your GP'
                  'T license, run the command \'source {}\' to reload your {} f'
                  'ile, and then try again.'
                  .format(self.bash_file, self.bash_file, self.bash_file))
            sys.exit(1)

    def detectBmad(self):
        DIST_BASE_DIR = os.getenv('DIST_BASE_DIR')
        if DIST_BASE_DIR is None:
            print('\033[1mfullbeamline: \033[31merror: \033[0mBmad not detected'
                  '. Source code and install instructions can be found at:\n'
                  ' https://www.classe.cornell.edu/~dcs/bmad/\nDon\'t forget to'
                  ' update your {} file as instructed.'
                  .format(self.bash_file))
            sys.exit(1)
        try:
            self.bmad_dir = pathlib.Path(DIST_BASE_DIR).resolve()
            self.bmad_exists = True
        except FileNotFoundError as e:
            print('\033[1mfullbeamline: \033[33mwarning: \033[0mShell variable'
                  ' \'DIST_BASE_DIR\' indicates Bmad directory is located at {}'
                  ', yet nothing exists at that path. If you moved the location'
                  ' of your Bmad directory, update your {} file and run the com'
                  'mand \'source {}\' to reload it.'
                  .format(DIST_BASE_DIR, self.bash_file, self.bash_file))
            self.bmad_dir = None
            self.bmad_exists = False

    def ensureTaoWorks(self):
        try:
            subprocess.run('tao -noinit -noplot', shell=True, check=True, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            print('\033[1mfullbeamline: \033[33merror: \033[0mCommand \'tao\' n'
                  'ot working. Either you forgot to put it in your PATH, or Bma'
                  'd is not compiled. To add Tao to your path, put the line \'e'
                  'xport PATH="$PATH:$DIST_BASE_DIR/debug/bin:$DIST_BASE_DIR/pr'
                  'oduction/bin"\' to your {} file. To build Bmad, run \'fullbe'
                  'amline --build debug\' or \'fullbeamline --build production'
                  '\''.format(self.bash_file))
            sys.exit(1)

    def detectCURL(self):
        try:
            subprocess.run('curl --version', shell=True, check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            warning('cURL not found.')
            print('\033[1mfullbeamline: \033[33merror: \033[0mcURL not installe'
                  'd. Please install cURL and make sure it is invokable with th'
                  'e command \'curl\'')
            sys.exit(1)


system_environment = SystemEnvironment()
