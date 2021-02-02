#!/usr/bin/python

import pandas as pd

original_list: pd.DataFrame = pd.read_csv("working/telegram.txt", delimiter="\t")
other_list: pd.DataFrame = pd.read_csv("working/subtract-telegramsub.txt", delimiter="\t")

remove: list = other_list["url"].to_list()

temp: pd.DataFrame = original_list.loc[~(original_list["url"].isin(remove))]
temp.reset_index(drop=True, inplace=True)

temp.to_csv("working/cleaned-telegram.csv", index=False)

print(temp)
