# CLEANATLANTIC
All the code of CleanAtlantic developed by INTECMAR

AIM:
----
The main goal of these programs is to count the beaching particles of the outputs of MOHID Langrangian model (old version) and insert in segments of coastlines. These segments are stored in PostGIS database.

Cambios:
--------

20201207
********

O proxecto actual funcionando de CleanAtlantic está no cartafol trunk. Ten un cartafol revisar que hai que tentar borrar.

O cartafol trunk ten os seguintes programas:

* acu2graf.py: programa sucio para crear os "termogramas" de acúmulos
* hdflitter.py: programa que conta as partículas de unha saida hdf5 e que están dentro de un buffer.
* hdflitter_agrega: programa que acumula días de cantidades que están dentro de un buffer na base de datos.
* insertbuffer.py: Inserta un buffer na base de datos a partir de un shapefile
* insertorde.py: engade unha táboa de ordenamento dos buffers.
* pegspeed.py: Read a hdf5 file and get the value of velocity on points and times from a csv dataframe

Estoy facendo unha restructuración e limpeza do código, e cada programa vai ir no seu cartafol. Por agora xa empecei con 
hdflitter.py
