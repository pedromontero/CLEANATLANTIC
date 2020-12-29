# CLEANATLANTIC
All the code of CleanAtlantic developed by INTECMAR

AIM:
----
The main goal of these programs is to count the beaching particles of the outputs of MOHID Langrangian model (old version) and insert in segments of coastlines. These segments are stored in PostGIS database.

SCRIPTS:
--------

- **hdflitter:** Count particles from a HDF5 MOHID Lagrangian file with LITTER option into
each poligon of a buffer stored in a CleanAtlantic Database, and insert the
results into the same db.
  
  
- **insertbuffer:** Insert origin, buffers and poligons reading a shapefile. It is  old fashion code


- **insertorde:** Insert a order table for some polygons of a buffer.


- **pegspeed:** Calculate the velocity of a peg, and the velocitiy from a MOHID Hydrodynamic
  output on the peg spots, and save the results in csv and xlsx format
  

- **windspeed:** Read a WRF output of wind and save the lefdown node matching the locations
  from a CSV file.
  

- **cleanatlantic:** Some libs for deal with buffers and partics, read mohid hdf files,
  and find ij from a lat, lon position
  

- **stuff:** Folder with old code
