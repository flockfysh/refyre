from pathlib import Path
import sys
import venv
import site
from refyre.utils import optional_dependencies
from refyre import Refyre
from pip._internal import main as pip_main
import subprocess
import shutil

def create_virtualenv_and_install_requirements(venv_path, requirements_file):
    # Create the virtual environment
    venv_builder = venv.EnvBuilder(with_pip=True)
    venv_builder.create(venv_path)

    # Activate the virtual environment
    activate_script = (
        Path(venv_path) / "Scripts" / "activate" if sys.platform == "win32"
        else Path(venv_path) / "bin" / "activate"
    )
    activate_cmd = f"source {activate_script} && python -m pip"
    
    # Install the requirements using pip within the virtual environment
    log("installing reqs")
    pip_install_cmd = f"{activate_cmd} install -r {requirements_file}"
    subprocess.run(pip_install_cmd, shell=True, check=True)

class RecipePreprocessor:
    def __new__(self, recipe_path):
        '''
            Performs all the recipe path preprocessing, and then 
            returns the Refyre instance
            to manage.

            Returns the refyre instance
        '''
        with optional_dependencies("warn"):
            import yaml 

            assert Path(recipe_path).exists(), f"The input file you were trying to access - {recipe_path} - does NOT exist"

            recipe_dict = None
            with open(recipe_path, 'r') as f:
                recipe_dict = yaml.safe_load(f)
            
            '''
            Currently, a recipe consists of attributes:

                input-spec: a filepath to the input spec
                base-dir: filepath to the base directory / entry point you want your program to see
                env: a description of the environment you want to setup, with two attributes
                    - name: name of the environment
                    - requirements: requirements file

            '''

            log(recipe_dict)
            log(recipe_dict['env']['name'])

            #Setup the base directories based on an input spec
            ref = Refyre.Refyre(input_specs = [recipe_dict["input-spec"]])

            #Create the env if it doesn't exist already or needs to be refreshed
            if 'env' in recipe_dict and recipe_dict['env']:
                if 'name' in recipe_dict['env']:
                    if not Path(recipe_dict['env']['name']).exists():
                        create_virtualenv_and_install_requirements(recipe_dict['env']['name'], recipe_dict['env']['requirements'])
                    elif 'refresh' in recipe_dict['env'] and recipe_dict['env']['refresh']:
                        shutil.rmtree(recipe_dict['env']['name'])
                        create_virtualenv_and_install_requirements(recipe_dict['env']['name'], recipe_dict['env']['requirements'])

            #Activate the env 
            activate_script = (
                Path(venv_path) / "Scripts" / "activate" if sys.platform == "win32"
                else Path(venv_path) / "bin" / "activate"
            )
            activate_cmd = f"source {activate_script}"
            subprocess.run(activate_cmd, shell=True, check=True)

            return ref
            

