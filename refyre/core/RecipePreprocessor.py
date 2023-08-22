from pathlib import Path
import sys
import venv
import site

from refyre.utils import optional_dependencies
from refyre import Refyre
from refyre.config import logger

from pip._internal import main as pip_main
import subprocess
import shutil
import os



def create_virtualenv_and_install_requirements(directory, requirements_file):
    """
    Create a virtual environment in the specified directory using venv.Builder.

    Args:
        directory (str): The directory path where the virtual environment will be created.
    """
    # Create the directory if it doesn't exist
    Path(directory).mkdir(parents=True, exist_ok=True)

    # Set up the builder
    builder = venv.EnvBuilder(with_pip=True)

    # Create the virtual environment
    builder.create(directory)



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
                logger.debug(recipe_dict)
            
            '''
            Currently, a recipe consists of attributes:

                input-spec: a filepath to the input spec
                base-dir: filepath to the base directory / entry point you want your program to see
                env: a description of the environment you want to setup, with two attributes
                    - name: name of the environment
                    - requirements: requirements file

            '''

            logger.debug(recipe_dict)
            logger.debug(recipe_dict['env']['name'])

            #Setup the base directories based on an input spec
            logger.debug(f'Sending to: {recipe_dict["input-spec"]}')


            #Current base directory is assumed to be CWD
            '''
            if 'base-dir' and Path(recipe_dict['base-dir']) != Path.cwd():
                current_base_dir = Path.cwd()

                logger.debug(f'{sys.path}, {current_base_dir.resolve()}')
                sys.path.remove(str(current_base_dir.resolve()))

                sys.path.append(str(Path(recipe_dict['base-dir'].resolve())))
                logger.debug()
            '''

            ref = Refyre.Refyre(input_specs = [recipe_dict["input-spec"]])

            #Create the env if it doesn't exist already or needs to be refreshed
            venv_path = recipe_dict['env']['name']
            if 'env' in recipe_dict and recipe_dict['env']:
                if 'name' in recipe_dict['env']:
                    if not Path(recipe_dict['env']['name']).exists():
                        create_virtualenv_and_install_requirements(venv_path, recipe_dict['env']['requirements'])
                    elif 'refresh' in recipe_dict['env'] and recipe_dict['env']['refresh']:
                        shutil.rmtree(recipe_dict['env']['name'])
                        create_virtualenv_and_install_requirements(recipe_dict['env']['name'], recipe_dict['env']['requirements'])


            return ref
            

