
import pandas as pd
import pycountry
import world_bank_data as wb
import matplotlib.pyplot as plt
import seaborn as sns

# Load Cell Data
cellsDF = pd.read_csv('./data/year_2018__cell_500k/squares_and_triangles/cells.csv')
num_LL_triangles = cellsDF.groupby(['CountryCode'])['LowerLeft'].agg('sum')
num_UR_triangles = cellsDF.groupby(['CountryCode'])['UpperRight'].agg('sum')
num_squares =      cellsDF.groupby(['CountryCode'])['IncludeInSquares'].agg('sum')
cellQty_sq_tri = pd.DataFrame((num_LL_triangles+num_UR_triangles)/2, columns=['qty'])
cellQty_sq = pd.DataFrame((num_squares)).rename(columns={'IncludeInSquares':'qty'})
cellQty = cellQty_sq_tri.join(cellQty_sq, lsuffix='_sqtri', rsuffix='_sq').reset_index()

# Append Alpha Country Code for population join
def Numeric2Alpha(num):
    return pycountry.countries.get(numeric=str(num).zfill(3)).alpha_3
cellQty['CountryAlpha3'] = cellQty['CountryCode'].apply(Numeric2Alpha)

# join population
wb_pop = pd.DataFrame(wb.get_series('SP.POP.TOTL', date='2018', id_or_value='id', simplify_index=True))
cellQty = cellQty.join(wb_pop, on='CountryAlpha3')

# plot the result
cellQty['hasTri'] = cellQty['SP.POP.TOTL']<3e5
cellQty.loc[cellQty['CountryAlpha3']=='ITA', 'hasTri'] = True

fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=2, figsize=(16,6))

sns.set(style="whitegrid")

sns.lineplot(x = [250e3,2e9], y = [0.5,4000], ax=ax1, color='#333333')
sns.scatterplot(x = "SP.POP.TOTL", y = "qty_sq", hue="hasTri", data=cellQty, ax=ax1, legend=False, palette=["#34495e", "#2ecc71"], linewidth=0, size=1.5)
plt.xscale("log")
plt.yscale("log")
ax1.title.set_text('Squares Only')
ax1.xaxis.set_label_text("True Population")
ax1.yaxis.set_label_text("Catrogram Cells")

ax1.set_xscale('log')
ax2.set_xscale('log')
ax1.set_yscale('log')
ax2.set_yscale('log')

sns.lineplot(x = [250e3,2e9], y = [0.5,4000], ax=ax2, color='#333333')
sns.scatterplot(x = "SP.POP.TOTL", y = "qty_sqtri", hue="hasTri", data=cellQty, ax=ax2, legend=False, palette=["#34495e", "#2ecc71"], linewidth=0, size=1.5)
plt.xscale("log")
plt.yscale("log")
ax2.title.set_text('Squares & Triangles')
ax2.xaxis.set_label_text("True Population")
ax2.yaxis.set_label_text("Catrogram Cells")

sns.set(style='whitegrid')

plt.savefig('./img/populationplot__year_2018__cell_500k.png')
