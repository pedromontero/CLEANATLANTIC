import sys
from collections import OrderedDict
import json
try:
    with open('../hdflitter.json', 'r') as f:
        inputs = json.load(f, object_pairs_hook=OrderedDict)
        orixe_name = inputs['origin']
        buffer_name = inputs['buffer']
        dt = inputs['acumulation_time']
        path_lags = inputs['path_lag_files']
        spin = inputs['spin']
        output = inputs['output']

        if "shp" in output:
            print(output["shp"])
        elif "db" in output:
            print(output["db"])
        else:
            raise Exception("Only one db or one shp is permited for the output key in hdflitter.json ")
except IOError:
    sys.exit('An error occured trying to read the file.')
except KeyError:
    sys.exit('An error with a key')
except ValueError:
    sys.exit('Non-numeric data found in the file.')
except Exception as err:
    print(err)
    sys.exit("Error with the input hdflitter.json")


