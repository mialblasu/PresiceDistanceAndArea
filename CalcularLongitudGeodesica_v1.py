#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:  Calcular longitudes verdaderas. (Geodesica + correccion
# de altura elipsoidal del area geografica a calcular)
#
# Author:      miguel blanco
#
# Created:     20/07/2020
# Copyright:   (c) miguel blanco miguelblancogeo@gmail.com
# Licence:     <MIGUEL BLANCO 2020>
#-------------------------------------------------------------------------------
import arcpy
from arcpy import env
from arcpy.sa import *

arcpy.env.overwriteOutput=True


# Set environment settings
env.workspace = r"D:\GISDRON\AD_Precisa\OrigenUnico.gdb"
Elipsoide = r"D:\GISDRON\AD_Precisa\ColElipsSRTM30_Geocol2004.tif"
# Elipsoide = r"D:\GISDRON\AD_Precisa\Elips_SRTM90m_geocol2004.tif"  REVISAR RENDIMIENTO CON PIX 90M

##arcpy.AddMessage ("Con Ellipsoide SRTM 30m........")
arcpy.AddMessage ("Calculo de longitudes con base en elipsoide y altura elipsoidal del segmento........")
##Altura = arcpy.GetParameterAsText(0)            # ELIMINAR
Capa = arcpy.GetParameterAsText(0)  # couche au format ligne

CamFactorD = "CFactorD"

CamDistG1 ="Distance"

#  CONSTANTE  *VARIAS FORMAS*
#  0.00000015716866611963   con plano medio - IGAC
#  0.000000157236131385584  con plano absoluto sobre el punto * elipsoide sacado de geoCol2004 - SRTM90 metros
#  0.00000015704909327841  Con metodo matematico formula de la norma NBR14166.pdf  http://www.carto.eng.uerj.br/cdecart/download/NBR14166.pdf

##constante = float(0.00000015704909327841)  #  matematico Norma NBR14166 *Brasil*

try:

    arcpy.DeleteFeatures_management("Centroides")
    arcpy.DeleteFeatures_management("CentroRaster")
except:
    pass

##arcpy.AddMessage ("Lineas a ceintroide........")
arcpy.FeatureToPoint_management(Capa, "Centroides","INSIDE")    # CENTROID  Attentoin au inside peu

##arcpy.AddMessage("Centroides Generado")

##arcpy.AddMessage ("Extrayendo Altura Elipsoidal del centroide........")
ExtractValuesToPoints("Centroides",Elipsoide,"CentroRaster","INTERPOLATE", "VALUE_ONLY")

# ## CALCULO DE DISTANCIA GEODESICA CON CORRECCION TOPOGRAFICA CON ALTURA CONSTANTE COMO EN PTL  # ##

arcpy.AddGeometryAttributes_management(Capa,"LENGTH_GEODESIC","METERS")


# ## CALCULO DE DISTANCIA CON ALTURA VARIABLE DE ACUERDO A ALTURA ELIPSOIDAL DEL TERRENO # ##


arcpy.AddField_management(Capa,CamFactorD,"FLOAT")   # Factor de correccion vertival de distancia
##arcpy.AddField_management(Capa,CamDistG,"DOUBLE")   #Distancia Geodesica correccion relieve como en PTL
arcpy.AddField_management(Capa,CamDistG1,"DOUBLE")  #Distancia Geodesica correccion relieve con correccion sobre elipsoide

##arcpy.AddMessage ("Uniendo Tablas........")

ListaCampos = arcpy.ListFields(Capa)

##arcpy.AddMessage(ListaCampos)

for f in ListaCampos:
    if f.name == "OBJECTID":
        arcpy.JoinField_management(Capa,"OBJECTID","CentroRaster","ORIG_FID","RASTERVALU")
    elif f.name == "OBJECTID_1":
        arcpy.JoinField_management(Capa,"OBJECTID_1","CentroRaster","ORIG_FID","RASTERVALU")



##arcpy.AddMessage ("Calculo Distancias geodesicas........")
calculoLG= "(0.00000015704909327841*!RASTERVALU!)+1.0"

arcpy.CalculateField_management(Capa,"CFactorD", calculoLG,"PYTHON")


CalculoLong="!LENGTH_GEO!*!CFactorD!"   #   formu1 ="!LENGTH_GEO!*"


##arcpy.AddMessage ("Calculo Distancia superprecisa........")
arcpy.CalculateField_management(Capa,CamDistG1,CalculoLong,"PYTHON")  #Capa   "Capajoin"

##arcpy.AddMessage ("Cleaning ........")
arcpy.DeleteField_management(Capa, ["LENGTH_GEO","CFactorD","RASTERVALU"])
