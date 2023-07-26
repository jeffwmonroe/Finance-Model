import pandas as pd

movies = pd.read_csv("documents\\movies.csv", index_col="Title")
print(movies)

print(movies.shape)
print(movies.size)
print(movies.dtypes)

print(movies.iloc[499])
print(movies.loc['Forrest Gump'])

movies.sort_values(by="Year", ascending=True)
