library(data.table)
library(ggplot2)
library(wbstats)
library(countrycode)
library(magick)
library(rcartocolor)

cellsDT   <- fread('https://raw.githubusercontent.com/mattdzugan/World-Population-Cartogram/master/data/year_2018__cell_500k/squares_and_triangles/cells.csv')
bordersDT <- fread('https://raw.githubusercontent.com/mattdzugan/World-Population-Cartogram/master/data/year_2018__cell_500k/squares_and_triangles/borders.csv')

cellsDT$CountryCodeAlpha <- countrycode(cellsDT$CountryCode, origin = "iso3n", destination = 'iso3c')


my_indicators <- c(
  fert = "SP.DYN.TFRT.IN"
  ,int = "IT.NET.BBND.P2"
  ,energy = "EG.USE.COMM.CL.ZS"
  ,numbeds = "SH.MED.BEDS.ZS"
)
d <- as.data.table(wb_data(my_indicators, start_date = 2000, gapfill = TRUE, mrv = 20))
cellsDT <- merge(cellsDT, d[date==2018, ], by.x='CountryCodeAlpha', by.y='iso3c', all.x=TRUE)


# map
gg_map<-ggplot()+
  theme_void()+
  theme(plot.background = element_rect(fill = "#ffffff")
        , legend.position = 'none'
        , plot.title = element_text(color="#111111", size=24, face="bold", hjust=0.5)
        , plot.margin=grid::unit(c(0,0,0,0), "mm"))+
  geom_tile(data=cellsDT,   aes(x=X+0.5, y=Y+0.5, fill=as.factor(CountryCode)), color=NA)+
  geom_path(data=bordersDT, aes(x=X, y=Y, group=PolygonID), size=0.25)+
  scale_fill_manual(values=rep(carto_pal(9,name = "Bold"), 100)) +
  coord_fixed()+
  labs(title = 'World Population Cartogram'
       , caption = 'Max Roser (2018) – "The map we need if we want to think about how global living conditions are changing". Published online at OurWorldInData.org. Retrieved from: ‘https://ourworldindata.org/world-population-cartogram’ [Online Resource]')

# fertility
gg_frt<-ggplot()+
  theme_void()+
  theme(plot.background = element_rect(fill = "#ffffff")
        , plot.margin=grid::unit(c(0,0,0,0), "mm")
        , plot.title = element_text(color="#111111", size=24, face="bold", hjust=0.5)
        , legend.position = 'none')+
  geom_tile(data=cellsDT,   aes(x=X+0.5, y=Y+0.5, fill=fert), color=NA)+
  geom_path(data=bordersDT, aes(x=X, y=Y, group=PolygonID), size=0.05, color="#ffffff")+
  coord_fixed()+
  scale_fill_carto_c(palette = 'Sunset')+
  labs(title = 'Fertility Rate by Country'
       , caption = 'Max Roser (2018) – "The map we need if we want to think about how global living conditions are changing". Published online at OurWorldInData.org. Retrieved from: ‘https://ourworldindata.org/world-population-cartogram’ [Online Resource]')


# energy
gg_enr<-ggplot()+
  theme_void()+
  theme(plot.background = element_rect(fill = "#ffffff")
        , plot.margin=grid::unit(c(0,0,0,0), "mm")
        , plot.title = element_text(color="#111111", size=24, face="bold", hjust=0.5)
        , legend.position = 'none')+
  geom_tile(data=cellsDT,   aes(x=X+0.5, y=Y+0.5, fill=(energy>10)), color=NA)+
  geom_path(data=bordersDT, aes(x=X, y=Y, group=PolygonID), color="#2d3436", size=0.2)+
  scale_fill_manual(values=c('#dfe6e9','#78e08f','#b2bec3'))+
  coord_fixed()+
  labs(title = 'Countries with at least 10% of Energy from Alternative Sources'
       , caption = 'Max Roser (2018) – "The map we need if we want to think about how global living conditions are changing". Published online at OurWorldInData.org. Retrieved from: ‘https://ourworldindata.org/world-population-cartogram’ [Online Resource]')
#scale_fill_viridis_c(option = 'A', direction = -1)


# internet
cellsDT$rand <- runif(nrow(cellsDT))
cellsDT[, hasInternet := 100*rand<int]
gg_int<-ggplot()+
  theme_void()+
  theme(plot.background = element_rect(fill = "#ffffff")
        , plot.margin=grid::unit(c(0,0,0,0), "mm")
        , plot.title = element_text(color="#111111", size=24, face="bold", hjust=0.5)
        , legend.position = 'none')+
  geom_tile(data=cellsDT,   aes(x=X+0.5, y=Y+0.5, fill=hasInternet), color=NA)+
  #geom_path(data=bordersDT, aes(x=X, y=Y, group=PolygonID), color="#0a3d62", size=0.2)+
  scale_fill_manual(values=c('#192a56','#00a8ff','#3c6382'))+
  coord_fixed()+
  labs(title = 'Proportion of World with High-Speed Broadband'
       , caption = 'Max Roser (2018) – "The map we need if we want to think about how global living conditions are changing". Published online at OurWorldInData.org. Retrieved from: ‘https://ourworldindata.org/world-population-cartogram’ [Online Resource]')


# numbeds
gg_bed<-ggplot()+
  theme_void()+
  theme(plot.background = element_rect(fill = "#ffffff")
        , plot.margin=grid::unit(c(0,0,0,0), "mm")
        , plot.title = element_text(color="#111111", size=24, face="bold", hjust=0.5)
        , legend.position = 'none')+
  geom_tile(data=cellsDT,   aes(x=X+0.5, y=Y+0.5, fill=numbeds<=1), color=NA)+
  scale_fill_manual(values = c("#ecf0f1","#f1c40f"))+
  geom_path(data=bordersDT, aes(x=X, y=Y, group=PolygonID), size=0.25, color='#34495e')+
  coord_fixed()+
  labs(title = 'Less than 1 Hospital Bed per 1000 people'
       , caption = 'Max Roser (2018) – "The map we need if we want to think about how global living conditions are changing". Published online at OurWorldInData.org. Retrieved from: ‘https://ourworldindata.org/world-population-cartogram’ [Online Resource]')



ggsave(filename = '../img/demo_map.png', plot = gg_map, width=16, height=7)
ggsave(filename = '../img/demo_frt.png', plot = gg_frt, width=16, height=7)
ggsave(filename = '../img/demo_enr.png', plot = gg_enr, width=16, height=7)
ggsave(filename = '../img/demo_int.png', plot = gg_int, width=16, height=7)
ggsave(filename = '../img/demo_bed.png', plot = gg_bed, width=16, height=7)
#image_write(image_trim(image_read('../img/demo_map.png')), '../img/demo_map.png')
#image_write(image_trim(image_read('../img/demo_frt.png')), '../img/demo_frt.png')
#image_write(image_trim(image_read('../img/demo_enr.png')), '../img/demo_enr.png')
#image_write(image_trim(image_read('../img/demo_int.png')), '../img/demo_int.png')
#image_write(image_trim(image_read('../img/demo_bed.png')), '../img/demo_bed.png')


# concat images
demo_set <- c(image_read('../img/demo_map.png')
              , image_read('../img/demo_frt.png')
              , image_read('../img/demo_enr.png')
              , image_read('../img/demo_int.png')
              , image_read('../img/demo_bed.png'))

image_write(image_append(image_scale(demo_set, "1600"), stack = TRUE)
            , '../img/demo.png')
image_write(image_animate(image_scale(demo_set, "1600"), fps = 0.5, dispose = "previous")
            , '../img/demo.gif')
