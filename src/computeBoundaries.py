import os
from shapely.geometry import Polygon as shpPolygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import pandas as pd
from geojson import Feature, Point, Polygon, MultiPolygon, FeatureCollection, dump


# list all tilings in the repos
tilingDirectories = os.listdir('data')

print('Creating All Square-Cell-Tilings from Square+Triangle-Cells-Tilings:')
for tilingDir in tilingDirectories:

    print(tilingDir)
    tilingPath = 'data/'+tilingDir+'/squares_and_triangles/cells.csv'

    # read initial cells.csv
    cellsDF = pd.read_csv(tilingPath)

    # write the squares one
    tilingPath = 'data/'+tilingDir+'/squares/cells.csv'
    cellsDF[['X','Y','CountryCode']].to_csv(tilingPath,index=False)

    print('All Square-Cell-Tilings Created.')
print('')





def CreatePolygon(row):
    if 'LowerLeft' in row.keys():
        # squares and triangles
        if (row['LowerLeft']&row['UpperRight']):
            return shpPolygon([(row['X'],   row['Y']),
                            (row['X']+1, row['Y']),
                            (row['X']+1, row['Y']+1),
                            (row['X'],   row['Y']+1)])
        elif (row['UpperRight']):
            return shpPolygon([(row['X'],   row['Y']+1),
                            (row['X']+1, row['Y']),
                            (row['X']+1, row['Y']+1)])
        else: #LowerLeft
            return shpPolygon([(row['X'],   row['Y']),
                            (row['X']+1, row['Y']),
                            (row['X'],   row['Y']+1)])
    else:
        return shpPolygon([(row['X'],   row['Y']),
                        (row['X']+1, row['Y']),
                        (row['X']+1, row['Y']+1),
                        (row['X'],   row['Y']+1)])


def BorderDf2BorderTuple(borderDF):
    myBorder = tuple((zip(borderDF.X/1000, borderDF.Y/1000)))
    return myBorder



print('Creating Border Data:')
for tilingDir in tilingDirectories:
    # for both squares and squares+triangles
    for tilingStyle in ['squares_and_triangles', 'squares']:
        tilingPath = 'data/'+tilingDir+'/'+tilingStyle+'/cells.csv'
        print(tilingDir + ' -- ' + tilingStyle)

        # load in cellsDF
        cellsDF = pd.read_csv(tilingPath)

        # get full set of country codes
        countryCodeList = pd.unique(cellsDF['CountryCode'])

        #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
        #   prepare to iterate country by country   #
        #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
        featureList = []
        polygonID = 0
        bordersDF = pd.DataFrame()
        for countryCode in countryCodeList:

            # select just the relevant country cells
            countryCellsDF = cellsDF.loc[cellsDF['CountryCode'] == countryCode]

            # create a dataframe of this country's polygons
            countryPolyDF = countryCellsDF.apply(CreatePolygon, axis=1)

            # now combine all squares into a single (multi-) Polygon
            unionPolygon = unary_union(countryPolyDF.tolist())

            # Now we need to handle "Polygon" vs "Multipolygon" differently
            if unionPolygon.geom_type=='Polygon':
                #-#-#-#-#-#-#-#
                #   Polygon   #
                #-#-#-#-#-#-#-#
                unionPolygon = orient(unionPolygon, -1)
                polygonID = polygonID+1

                # popualte DF with data
                borderDF = pd.DataFrame(unionPolygon.exterior.coords[:], columns=["X","Y"])
                borderDF['PolygonID'] = polygonID
                borderDF['CountryCode'] = countryCode
                borderDF['BorderType'] = "Exterior"

                # initiate JSON object
                myPolyBorders = []

                # populate JSON with data
                myBorder = BorderDf2BorderTuple(borderDF)
                myPolyBorders.append(myBorder)

                # if there's a hole on the inside of our polygon - add that
                if len(unionPolygon.interiors)>0:
                    for intpoly in unionPolygon.interiors:
                        polygonID = polygonID+1
                        intborderDF = pd.DataFrame(intpoly.coords[:], columns=["X","Y"])
                        intborderDF['PolygonID'] = polygonID
                        intborderDF['CountryCode'] = countryCode
                        intborderDF['BorderType'] = "Interior"
                        borderDF = pd.concat([borderDF, intborderDF])
                        #
                        myInnerBorder = BorderDf2BorderTuple(intborderDF)
                        myPolyBorders.append(myInnerBorder)

                # finalize DF and JSON before leaving loop
                newBorderDF = borderDF
                myP = Polygon(myPolyBorders)
                myF = Feature(geometry=myP, properties={"id": str(countryCode)+'--'+str(polygonID)})

            else:
                #-#-#-#-#-#-#-#-#-#
                #   MultiPolygon  #
                #-#-#-#-#-#-#-#-#-#
                allborderDF = pd.DataFrame()
                myMultiPolyPolys = [] # initiate JSON object (MultiPolygon)

                for geom in unionPolygon.geoms:
                    geom = orient(geom, -1)
                    polygonID = polygonID+1
                    borderDF = pd.DataFrame(geom.exterior.coords[:], columns=["X","Y"])
                    borderDF['PolygonID'] = polygonID
                    borderDF['CountryCode'] = countryCode
                    borderDF['BorderType'] = "Exterior"

                    # initiate JSON object (Polygon)
                    myPolyBorders = []

                    # populate JSON with data
                    myBorder = BorderDf2BorderTuple(borderDF)
                    myPolyBorders.append(myBorder)

                    if len(geom.interiors)>0:
                        for intpoly in geom.interiors:
                            polygonID = polygonID+1
                            intborderDF = pd.DataFrame(intpoly.coords[:], columns=["X","Y"])
                            intborderDF['PolygonID'] = polygonID
                            intborderDF['CountryCode'] = countryCode
                            intborderDF['BorderType'] = "Interior"
                            borderDF = pd.concat([borderDF, intborderDF])
                            #
                            myInnerBorder = BorderDf2BorderTuple(intborderDF)
                            myPolyBorders.append(myInnerBorder)
                    allborderDF = pd.concat([allborderDF, borderDF])
                    myMultiPolyPolys.append(myPolyBorders)

                # finalize DF and JSON before leaving loop
                newBorderDF = allborderDF
                myMP = MultiPolygon(myMultiPolyPolys)
                myF = Feature(geometry=myMP, properties={"id": str(countryCode)+'--'+str(polygonID)})

            # add this new country's dataframe onto the aggregate dataframe
            bordersDF = pd.concat([bordersDF, newBorderDF])
            featureList.append(myF)

        # now write everything to file for each tiling
        # First, the "borders.csv"
        bordersDF.to_csv('data/'+tilingDir+'/'+tilingStyle+'/borders.csv', index=False)
        # Next, the "geo.json"
        feature_collection = FeatureCollection(featureList)
        geojson_path = 'data/'+tilingDir+'/'+tilingStyle+'/geo.json'
        with open(geojson_path, 'w', encoding ='utf8') as geojson_file:
            dump(feature_collection, geojson_file)
        # Finally the "projected.geo.json", the "topo.json", and the "countries.svg"
        projected_geojson_path   = 'data/'+tilingDir+'/'+tilingStyle+'/projected_geo.json'
        projected_countries_path = 'data/'+tilingDir+'/'+tilingStyle+'/countries.svg'
        topojson_path            = 'data/'+tilingDir+'/'+tilingStyle+'/topo.json'
        os.system("geoproject 'd3.geoEquirectangular().fitSize([1000, 500], d)' < " + geojson_path + " > " + projected_geojson_path)
        os.system("geo2svg -w 1000 -h 500 < " + projected_geojson_path + " > " + projected_countries_path)
        os.system("geo2topo countries="+projected_geojson_path+" \
        | toposimplify -p 0.0005 \
        | topoquantize 1e9 > " + topojson_path)

    
