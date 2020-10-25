import os
from shapely.geometry import Polygon
from shapely.ops import unary_union
import pandas as pd
import numpy as np
from geojson import Feature, Point, Polygon, MultiPolygon, FeatureCollection, dump



borderDF = pd.read_csv("./borders.csv")


borderDF = borderDF.loc[borderDF['CountryCode']<23,:] # CountrCode 20 is breaking this
#borderDF = borderDF.loc[np.isin(borderDF['CountryCode'],[792,124,196,422,275]),:]



featureList = []
for myCountryCode in np.unique(borderDF.CountryCode):
    myCountryDF = borderDF.loc[borderDF['CountryCode'] == myCountryCode, :]
    # myMultiPoly = []
    for myPolygonID in np.unique(myCountryDF.PolygonID):
        print(str(myCountryCode)+", "+str(myPolygonID))
        myBorderDF = myCountryDF.loc[myCountryDF['PolygonID'] == myPolygonID, :]
        #print(myBorderDF['BorderType'].values[0])
        if (myBorderDF['BorderType'].values[0] == 'Exterior'):
            #if (myCountryDF.shape[0] == 5):
                #myBorderDF = myBorderDF.reindex(index=myBorderDF.index[::-1])
            myBorderDF = myBorderDF.reindex(index=myBorderDF.index[::-1])
            myBorder = tuple((zip(myBorderDF.X/1000, myBorderDF.Y/1000)))
            myMP = MultiPolygon([
                ([myBorder]) # end of polygon
            ])
            myF = Feature(geometry=myMP, properties={"id": str(myCountryCode)+'--'+str(myPolygonID)})
            featureList.append(myF)
    #myMP = MultiPolygon([tuple(myMultiPoly)])
    #myMP = MultiPolygon(myMultiPoly)
    #myF  = Feature(geometry=myMP, properties={"country": str(myCountryCode)})
    #featureList.append(myF)
feature_collection = FeatureCollection(featureList)
#feature_collection



with open('test_geo.json', 'w', encoding ='utf8') as geojson_file:
    dump(feature_collection, geojson_file)



os.system("geoproject 'd3.geoEquirectangular().fitSize([960, 960], d)' < test_geo.json > projected_geo.json")
os.system("geo2svg -w 960 -h 960 < projected_geo.json > test_geo.svg")
