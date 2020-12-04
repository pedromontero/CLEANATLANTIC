"""

customize.py

@Purpose: Add custom lib path to modules
@version: 1.2

@python version: 3.4
@author: Pedro Montero
@license: INTECMAR
@requires:
@use: 1) copy customize.py to main python script path.
      2) change path changing computer_name
      3) include next lines before call any intecmar library in the main program:

            from customize import add_lib
            add_lib()

      4) import intecmar library. ex:

            from intecmar.fichero import input_file

@date 2015/04/23
@history:  v1.1 2015/04/28 Add new paths PMV
           v1.2 2016/03/15 Add model_ws_1 path
           v1.3 2016/09/28 Add model_ws_2 path

"""


def add_lib():
    """ Function to add paths, uncomment your computer_name"
    :return:
    """
    import sys

    # Uncomment your option

    computer_name = 'xefe_model_1'
    # computer_name = 'svr_model_1'
    # computer_name = 'model_ws_1'


    rutas = {'svr_model_1': r"C:\Users\usrsvrmodel\Documents\PYTHON\PRODUCCION\Libs",
             'xefe_model_1': r"C:\Users\UsrXModel1\Documents\02_TRABALLO\02_PYTHON\PRODUCCION\Libs",
             'model_ws_1': r"C:\Users\UMOUDAC\Documents\PYTHON\PRODUCCION\Libs",
             'model_ws_2': r"C:\Users\UMOUDAC\Documents\PYTHON\PRODUCCION\Libs",
             }
    ruta_libreria = rutas[computer_name]
    # ruta_libreria_externa = ruta_libreria + "\externas"
    sys.path.append(ruta_libreria)
    # sys.path.append(ruta_libreria_externa)
