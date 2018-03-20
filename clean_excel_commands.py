import pandas

class DataFrameClean:
    def __init__(self, filepath, diction):
        self.filepath = filepath
        self.df = pandas.read_csv(self.filepath)
        self.diction = diction

    def text_df(self, x):
        return x.lower

    def integer_df(self, x):
        return x + 1000

    def create_new_df(self):
        df_new = pandas.DataFrame()
        for i in self.df.columns:
            if i in self.diction:
                if self.diction[i] == 'integer':
                    df_new[i] = self.df[i].apply(self.integer_df)
                elif self.diction[i] == 'text':
                    df_new[i] = self.df[i].apply(self.text_df)
            else:
                df_new[i] = self.df[i]
        return df_new.to_csv()
