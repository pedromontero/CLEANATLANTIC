# CLEANATLANTIC
All the code of CleanAtlantic developed by INTECMAR

AIM:
----
The main goal of these programs is to count the beaching particles of the outputs of MOHID Langrangian model (old version) and insert in segments of coastlines. These segments are stored in PostGIS database.

SCRIPTS:
--------

hdflitter
*********

Count particles from a HDF5 MOHID Lagrangian file with LITTER option into
each poligon of a buffer stored in a CleanAtlantic Database, and insert the
results into the same db.

hdflitter
*********
