#Project that reconciles data by creating combinations of financial ledger data to agree to reconciling items
#in a report



import pandas as pd
import itertools
from bisect import bisect_left

class FindCombination():

    """
    Provide a dataframe and a
    list of items that you are trying to get the combination for

    """

    def __init__(self, df, lquery):
        self.df = df
        self.lquery = lquery

    def takeClosest(self, myList, myNumber):
        pos = bisect_left(myList, myNumber)
        if pos == 0:
            return myList[0]
        if pos == len(myList):
            return myList[-1]
        before = myList[pos - 1]
        after = myList[pos]
        if after - myNumber < myNumber - before:
            return after
        else:
            return before

    def get_combination_list(self):
        comb_dict = {}
        count =0
        for i in range(0, len(self.lquery)):
            for L in range(0,len(self.df)+1):
                for subset in itertools.combinations(self.df['Account'], L):
                    comb_dict["item" + str(self.lquery[i]) + "combination " +str(count) ] = [sum(list(subset)), subset]
                    count = count +1
        total_list = [comb_dict[key][0] for key in comb_dict.keys()]
        total_list.sort()
        return total_list

    def get_combination_dict(self):
        comb_dict = {}
        count =0
        for i in range(0, len(self.lquery)):
            for L in range(0,len(self.df)+1):
                for subset in itertools.combinations(self.df['Account'], L):
                    comb_dict["Item: " + str(self.lquery[i]) + "Combination#: " +str(count) ] = [sum(list(subset)), subset]
                    count = count +1
        total_list = [comb_dict[key][0] for key in comb_dict.keys()]
        total_list.sort()
        return comb_dict

    def get_closest(self):
        closests_matches = [self.takeClosest(self.get_combination_list(), self.lquery[i]) for i in range(0,len(self.lquery))]
        return closests_matches

    def create_comb_df(self):
        df2 = pd.DataFrame(columns=['set', 'total', 'combination'])
        comb_dict = self.get_combination_dict()
        count = 0
        for key in comb_dict.keys():
            df2.loc[count] = key
            df2.loc[count]['set'] = key
            df2.loc[count]['total'] = comb_dict[key][0]
            df2.loc[count]['combination'] = comb_dict[key][1]
            count = count +1
        return df2

    def create_comb_matchest(self):
        df2 = self.create_comb_df()
        df3 = pd.DataFrame(columns=['set', 'total', 'combination'])
        for i in range(0,len(self.lquery)):
                query = self.lquery[i]
                df3 = df3.append(df2[(df2['set'].str.contains(str(query))) & (df2['total'] == self.get_closest()[i])])
        df3.set_index('set', inplace=True)
        return df3

class FindCombinationList():

    """
    Provide a dataframe and a
    list of items that you are trying to get the combination for

    """

    def __init__(self, item_list, lquery):
        self.df = pd.DataFrame(item_list, columns=['Account'])
        self.lquery = lquery

    def takeClosest(self, myList, myNumber):
        pos = bisect_left(myList, myNumber)
        if pos == 0:
            return myList[0]
        if pos == len(myList):
            return myList[-1]
        before = myList[pos - 1]
        after = myList[pos]
        if after - myNumber < myNumber - before:
            return after
        else:
            return before

    def get_combination_list(self):
        comb_dict = {}
        count =0
        for i in range(0, len(self.lquery)):
            for L in range(0,len(self.df)+1):
                for subset in itertools.combinations(self.df['Account'], L):
                    comb_dict["item" + str(self.lquery[i]) + "combination " +str(count) ] = [sum(list(subset)), subset]
                    count = count +1
        total_list = [comb_dict[key][0] for key in comb_dict.keys()]
        total_list.sort()
        return total_list

    def get_combination_dict(self):
        comb_dict = {}
        count =0
        for i in range(0, len(self.lquery)):
            for L in range(0,len(self.df)+1):
                for subset in itertools.combinations(self.df['Account'], L):
                    comb_dict["Item: " + str(self.lquery[i]) + " Combination#: " +str(count) ] = [sum(list(subset)), subset]
                    count = count +1
        total_list = [comb_dict[key][0] for key in comb_dict.keys()]
        total_list.sort()
        return comb_dict

    def get_closest(self):
        closests_matches = [self.takeClosest(self.get_combination_list(), self.lquery[i]) for i in range(0,len(self.lquery))]
        return closests_matches

    def create_comb_df(self):
        df2 = pd.DataFrame(columns=['set', 'total', 'combination'])
        comb_dict = self.get_combination_dict()
        count = 0
        for key in comb_dict.keys():
            df2.loc[count] = key
            df2.loc[count]['set'] = key
            df2.loc[count]['total'] = comb_dict[key][0]
            df2.loc[count]['combination'] = comb_dict[key][1]
            count = count +1
        return df2

    def create_comb_matchest(self):
        df2 = self.create_comb_df()
        df3 = pd.DataFrame(columns=['set', 'total', 'combination'])
        for i in range(0,len(self.lquery)):
                query = self.lquery[i]
                df3 = df3.append(df2[(df2['set'].str.contains(str(query))) & (df2['total'] == self.get_closest()[i])])
        df3.set_index('set', inplace=True)
        return df3

    def create_comb_matchest_html(self):
        df2 = self.create_comb_df()
        df3 = pd.DataFrame(columns=['set', 'total', 'combination'])
        for i in range(0,len(self.lquery)):
                query = self.lquery[i]
                df3 = df3.append(df2[(df2['set'].str.contains(str(query))) & (df2['total'] == self.get_closest()[i])])
        df3.set_index('set', inplace=True)
        html = df3.to_html()
        return html
