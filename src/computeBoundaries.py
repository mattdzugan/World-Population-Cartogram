
from os import listdir
from shapely.geometry import Polygon
from shapely.ops import unary_union
import pandas as pd
from geojson import Feature, Point, FeatureCollection
            

# list all tilings in the repos
tilingDirectories = listdir('data')

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
            return Polygon([(row['X'],   row['Y']),
                            (row['X']+1, row['Y']),
                            (row['X']+1, row['Y']+1),
                            (row['X'],   row['Y']+1)])
        elif (row['UpperRight']):
            return Polygon([(row['X'],   row['Y']+1),
                            (row['X']+1, row['Y']),
                            (row['X']+1, row['Y']+1)])
        else: #LowerLeft
            return Polygon([(row['X'],   row['Y']),
                            (row['X']+1, row['Y']),
                            (row['X'],   row['Y']+1)])
    else:
        return Polygon([(row['X'],   row['Y']),
                        (row['X']+1, row['Y']),
                        (row['X']+1, row['Y']+1),
                        (row['X'],   row['Y']+1)])


    
def Polygon2DF(polygon):
    
    if unionPolygon.geom_type=='Polygon':
        polygonID = 1
        borderDF = pd.DataFrame(unionPolygon.exterior.coords, columns=["X","Y"])
        borderDF['PolygonID'] = polygonID
        borderDF['CountryCode'] = countryCode
        borderDF['BorderType'] = "Exterior"

        if len(unionPolygon.interiors)>0:
            for intpoly in unionPolygon.interiors:
                polygonID = polygonID+1
                print(countryCode)
                intborderDF = pd.DataFrame(intpoly.coords, columns=["X","Y"])
                intborderDF['PolygonID'] = polygonID
                intborderDF['CountryCode'] = countryCode
                intborderDF['BorderType'] = "Interior"
                borderDF = pd.concat([borderDF, intborderDF])
        
        return borderDF
    else:
        allborderDF = pd.DataFrame()
        polygonID = 0
        for geom in unionPolygon.geoms: 
            polygonID = polygonID+1
            borderDF = pd.DataFrame(geom.exterior.coords, columns=["X","Y"])
            borderDF['PolygonID'] = polygonID
            borderDF['CountryCode'] = countryCode
            borderDF['BorderType'] = "Exterior"

            if len(geom.interiors)>0:
                for intpoly in geom.interiors:
                    polygonID = polygonID+1
                    print(countryCode)
                    intborderDF = pd.DataFrame(intpoly.coords, columns=["X","Y"])
                    intborderDF['PolygonID'] = polygonID
                    intborderDF['CountryCode'] = countryCode
                    intborderDF['BorderType'] = "Interior"
                    borderDF = pd.concat([borderDF, intborderDF])
            allborderDF = pd.concat([allborderDF, borderDF])
        return allborderDF
    
    


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
        
        featureList = []
        maxPolygonID = 0
        bordersDF = pd.DataFrame()
        for countryCode in countryCodeList:
            countryDF = cellsDF.loc[cellsDF['CountryCode'] == countryCode]
            
            countryPolyDF = countryDF.apply(CreatePolygon, axis=1)
            unionPolygon = unary_union(countryPolyDF.tolist())
            newBorderDF = Polygon2DF(unionPolygon)
            newBorderDF["PolygonID"] = newBorderDF["PolygonID"]+maxPolygonID
            bordersDF = pd.concat([bordersDF, newBorderDF])
            maxPolygonID = max(bordersDF["PolygonID"])
            myFeature = Feature(geometry=unionPolygon, properties={"CountryCode": str(countryCode)})
            featureList.append(myFeature)
            
        feature_collection = FeatureCollection(featureList)
        bordersDF.to_csv('data/'+tilingDir+'/'+tilingStyle+'/borders.csv', index=False)
            
    


    
    


