geeSEBAL is a open-source implementation of Surface Energy Balance Algorithm for Land (SEBAL) using Google Earth Engine (GEE). geeSEBAL is available in both Javascript and Python API.\
\
This code is an edited version of geeSEBAL to achive the following objectives:
1. Replace outdated landsat collection 1 with landsat collection 2.
2. Add bands and functions to perform additional analysis and visualization.

\
Original geeSEBAL: (https://github.com/gee-hydro/geeSEBAL)
## How to use Google Earth Engine?

You need an account in GEE (https://earthengine.google.com/).
 
### Python API

Using pip to install earthengine-api

pip install earthengine-api
Authenticate Earth Engine library
import ee; ee.Authenticate()
## What is SEBAL?

Surface Energy Balance Algorithm for Land (SEBAL) was developed and validated by Bastiaanssen (Bastiaanssen, 1995; Bastiaanssen et al., 1998a, 1998b) to 
estimate evapotranspiration (ET) from energy balance equation (Rn – G = LE + H), where LE, Rn, G and H are Latent Heat Flux, Net Radiation, Soil Heat Flux and Sensible Heat Flux, respectively.

## Edits on the original code
1. Replaced landsat collection 1 with landsat collection 2.
2. Add potential evapotranspiration band.
3. Add actual evapotranspiration / potential evapotranspiration band.
4. Export functions for real colors, actual evapotranspiration, potential evapotranspiration, NDVI, actual evapotranspiration / potential evapotranspiration. Exports:\
a. Raw png images.\
b. Layout map images.\
c. Time-series charts.\
d. Time-series csv.\
e. Prief layout that contains the area shape in addition to the important charts and images.
5. Season notebook, that produce irrigation analysis for selected area throw growing season.

prief images example:\
![alt text](https://github.com/M-salah-8/geeSEBAL_ls8_c2/blob/master/brief.png)

## How to use season notebook
### Input
1. Make a shapefile for the project and another one for the field to be observed inside the project (use just one shapefile if the field cover the whole area of interest). Put the shapefiles in a folder then put your folder in (>shapefile) folder (if it's your first time make th shapefile folder).
2. Use suitable crop coefficient (Kc) in a csv file (see the example in kc folder) and put it in (>kc) folder.
3. Open (inputs.csv) (located in the main folder). Adjust names, dates and folder locations according to your inputs.
### Run the code
Make sure to download required packages and authenticate gee account.
### Outputs
1. Tif outputs go to google drive in a folder with the project name and date of creation.
2. Other outputs in >data folders in a folder with the project name.

## References
 [Laipelt et al. (2021)] Long-term monitoring of evapotranspiration using the SEBAL algorithm and Google Earth Engine cloud computing. (https://doi.org/10.1016/j.isprsjprs.2021.05.018)
