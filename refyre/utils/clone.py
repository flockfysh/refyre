from refyre.utils import optional_dependencies 
from refyre.cluster import FileCluster #Time to use the power of our variables :)
from pathlib import Path
from refyre.config import logger
import random
import shutil

def clone_node(url, fp):
    import git 

    logger.debug(f"GEET {git}")


    #Ensure no file conflicts
    rand_num = ''.join(["{}".format(random.randint(0, 9)) for num in range(0, 20)])
    tmp_empty = fp / f'tmp{rand_num}'


    logger.debug(f'Cloning to {tmp_empty}')
    git.Repo.clone_from(url, tmp_empty)

    mv_var = FileCluster(input_paths = [tmp_empty], input_patterns = ['g*'])

    mv_var.move(tmp_empty.parent)

    tmp_empty.rmdir()
