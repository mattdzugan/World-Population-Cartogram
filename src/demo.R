library(data.table)
library(ggplot2)
library(wbstats)
library(countrycode)
library(magick)

bordersDT <- fread('../data/year_2018__cell_500k/squares/borders.csv')
cellsDT   <- fread('../data/year_2018__cell_500k/squares/cells.csv')

cellsDT$CountryCodeAlpha <- countrycode(cellsDT$CountryCode, origin = "iso3n", destination = 'iso3c')


my_indicators <- c(
  fert = "SP.DYN.TFRT.IN"
  ,int = "IT.NET.BBND.P2"
  ,energy = "EG.USE.COMM.CL.ZS"
)
d <- as.data.table(wb_data(my_indicators, start_date = 2000, gapfill = TRUE, mrv = 20))
cellsDT <- merge(cellsDT, d[date==2018, ], by.x='CountryCodeAlpha', by.y='iso3c', all.x=TRUE)


# map
gg_map<-ggplot()+
  theme_void()+
  theme(plot.background = element_rect(fill = "#eeeeee")
        , legend.position = 'none'
        , plot.title = element_text(color="#111111", size=16, face="bold", hjust=0.5)
        , plot.margin=grid::unit(c(0,0,0,0), "mm"))+
  geom_tile(data=cellsDT,   aes(x=X+0.5, y=Y+0.5, fill=as.factor(CountryCode)), color="#ffffff33")+
  geom_path(data=bordersDT, aes(x=X, y=Y, group=PolygonID))+
  coord_fixed()+
  labs(title = 'World Population Cartogram')

# fertility
gg_frt<-ggplot()+
  theme_void()+
  theme(plot.background = element_rect(fill = "#ffeeee")
        , plot.margin=grid::unit(c(0,0,0,0), "mm")
        , plot.title = element_text(color="#130f40", size=16, face="bold", hjust=0.5)
        , legend.position = 'none')+
  geom_tile(data=cellsDT,   aes(x=X+0.5, y=Y+0.5, fill=fert), color=NA)+
  coord_fixed()+
  scale_fill_viridis_c(option = 'A', direction = -1)+
  labs(title = 'Fertility Rate by Country')


# energy
gg_enr<-ggplot()+
  theme_void()+
  theme(plot.background = element_rect(fill = "#dfe6e9")
        , plot.margin=grid::unit(c(0,0,0,0), "mm")
        , plot.title = element_text(color="#111111", size=16, face="bold", hjust=0.5)
        , legend.position = 'none')+
  geom_tile(data=cellsDT,   aes(x=X+0.5, y=Y+0.5, fill=(energy>10)), color=NA)+
  geom_path(data=bordersDT, aes(x=X, y=Y, group=PolygonID), color="#2d3436")+
  scale_fill_manual(values=c('#636e72','#00b894','#b2bec3'))+
  coord_fixed()+
  labs(title = 'Countries with at least 10% of Energy from Alternative Sources')
#scale_fill_viridis_c(option = 'A', direction = -1)


# internet
cellsDT$rand <- runif(nrow(cellsDT))
cellsDT[, hasInternet := 100*rand<int]
gg_int<-ggplot()+
  theme_void()+
  theme(plot.background = element_rect(fill = "#2d3436")
        , plot.margin=grid::unit(c(0,0,0,0), "mm")
        , plot.title = element_text(color="#dfe6e9", size=16, face="bold", hjust=0.5)
        , legend.position = 'none')+
  geom_tile(data=cellsDT,   aes(x=X+0.5, y=Y+0.5, fill=hasInternet), color=NA)+
  geom_path(data=bordersDT, aes(x=X, y=Y, group=PolygonID), color="#2d3436")+
  scale_fill_manual(values=c('#636e72','#74b9ff','#b2bec3'))+
  coord_fixed()+
  labs(title = 'Proportion of Country with High-Speed Broadband')


ggsave(filename = '../img/demo_map.png', plot = gg_map)
ggsave(filename = '../img/demo_frt.png', plot = gg_frt)
ggsave(filename = '../img/demo_enr.png', plot = gg_enr)
ggsave(filename = '../img/demo_int.png', plot = gg_int)
image_write(image_trim(image_read('../img/demo_map.png')), '../img/demo_map.png')
image_write(image_trim(image_read('../img/demo_frt.png')), '../img/demo_frt.png')
image_write(image_trim(image_read('../img/demo_enr.png')), '../img/demo_enr.png')
image_write(image_trim(image_read('../img/demo_int.png')), '../img/demo_int.png')


# concat images
demo_set <- c(image_read('../img/demo_map.png')
              , image_read('../img/demo_frt.png')
              , image_read('../img/demo_enr.png')
              , image_read('../img/demo_int.png'))

image_write(image_append(image_scale(demo_set, "400"), stack = TRUE)
            , '../img/demo.png')
image_write(image_animate(image_scale(demo_set, "800"), fps = 1, dispose = "previous")
            , '../img/demo.gif')


