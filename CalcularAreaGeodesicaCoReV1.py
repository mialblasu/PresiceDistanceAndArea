#-------------------------------------------------------------------------------
# Name:        Area and lengh precise calculations
# Purpose:     The goal is optain area and lengh calculatiosn in a very precise
#               methode like a topographic real measure using heigth precise
#               instruments. That means in fact not use of projectios.
#
# Author:      Miguel Blanco
#
# Created:     20/07/2020
# Copyright:   (c) migue 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------


# import system modules
import arcpy
from arcpy import env
from arcpy.sa import *

arcpy.env.overwriteOutput=True

# Set environment settings
env.workspace = r"D:\GISDRON\AD_Precisa\OrigenUnico.gdb"
Elipsoide = r"D:\GISDRON\AD_Precisa\ColElipsSRTM30_Geocol2004.tif"
# Elipsoide = r"D:\GISDRON\AD_Precisa\Elips_SRTM90m_geocol2004.tif"  REVISAR RENDIMIENTO CON PIX 90M



Capa = arcpy.GetParameterAsText(0)

arcpy.AddMessage ("Inicio de calculo preciso")             

CampoGeod1="Area_m2"
CampoFactor="CFactor"
CamFactorD = "CFactorD"
CamDistG1 ="Perime_m"

# 0.000000314337332239271  Con plano medio
# 0.000000314472262771167  Con altura absoluta sobre el punto
# 0.00000031409818655681 Basado en matematicas de NBR14166

##arcpy.AddMessage ("ModificacionDomingo........")
try:

    arcpy.DeleteFeatures_management("Centroides")
    arcpy.DeleteFeatures_management("CentroRaster")
except:
    pass


##arcpy.AddMessage ("Poligonos a ceintroide........")
arcpy.FeatureToPoint_management(Capa, "Centroides","INSIDE")    # CENTROID

##arcpy.AddMessage ("Extrayendo Altura Elipsoidal del centroide........")
ExtractValuesToPoints("Centroides",Elipsoide,"CentroRaster","INTERPOLATE", "VALUE_ONLY")


##arcpy.AddMessage ("Calculando Area Geodesica........")
arcpy.AddGeometryAttributes_management(Capa,"AREA_GEODESIC","METERS")  # Se genera un campo denominado "AREA_GEO"

##arcpy.AddMessage ("Calculando Perimetros Geodesicos........")
arcpy.management.AddGeometryAttributes(Capa,"PERIMETER_LENGTH_GEODESIC", "METERS") # Resultado es campo "PERIM_GEO"


arcpy.AddField_management(Capa,CampoGeod1,"DOUBLE")   # Area Geodesica correccion relieve con correccion sobre elipsoide
arcpy.AddField_management(Capa,CampoFactor,"FLOAT")   # Factor de correccion vertival de area
arcpy.AddField_management(Capa,CamFactorD,"FLOAT")   # Factor de correccion vertival de distancia
arcpy.AddField_management(Capa,CamDistG1,"DOUBLE")  #Distancia Geodesica correccion relieve con correccion sobre elipsoide

ListaCampos = arcpy.ListFields(Capa)

##arcpy.AddMessage(ListaCampos)

for f in ListaCampos:
    if f.name == "OBJECTID":

        arcpy.JoinField_management(Capa,"OBJECTID","CentroRaster","ORIG_FID","RASTERVALU")
    elif f.name == "OBJECTID_1":
        arcpy.JoinField_management(Capa,"OBJECTID_1","CentroRaster","ORIG_FID","RASTERVALU")


##expr = "100.0 *  !SUM_AREA! / {}".format(fieldsum)
calculo= "(0.00000031409818655681*!RASTERVALU!)+1.0"
##arcpy.CalculateField_management(Capa,CampoFactor,'"(!RASTERVALU!*0.00000031409818655681)+1.00"',"PYTHON")

arcpy.CalculateField_management(Capa,"CFactor", calculo,"PYTHON") #

##arcpy.CalculateField_management("Capajoin","CampFactor", calculo,"PYTHON") Cuando se utiliza spatial joint
# para geodesicas superprecisas

calculoPr= "!AREA_GEO!*!CFactor!"

arcpy.AddMessage ("Calculo area superprecisa.......")
arcpy.CalculateField_management(Capa,CampoGeod1,calculoPr,"PYTHON")  #Capa   "Capajoin"


# CALCULO PERIMETRO GEODESICO Y CORRECCION TOPOGRAFICA # ####################
# #######################################################################

##arcpy.AddMessage ("Calculo Perimetro super preciso........")
calculoLG= "(0.000000157236131385584*!RASTERVALU!)+1.0"

arcpy.CalculateField_management(Capa,"CFactorD", calculoLG,"PYTHON")


CalculoLong="!PERIM_GEO!*!CFactorD!"

arcpy.CalculateField_management(Capa,"CFactorD", calculoLG,"PYTHON")
##

arcpy.AddMessage ("Calculo Perimetro superprecisa........")
arcpy.CalculateField_management(Capa,CamDistG1,CalculoLong,"PYTHON")  #Capa   "Capajoin"

arcpy.AddMessage ("Cleaning ........")
arcpy.DeleteField_management(Capa, ["AREA_GEO","PERIM_GEO","CFactor","CFactorD","RASTERVALU"])
