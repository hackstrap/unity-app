#helper functions


"""
Calculates the percent change of a column in a dataframe
"""
def pct_change(df_column):

    return ((df_column - df_column.shift(1)) / df_column.shift(1) * 100)



def pct_change(df_column1, df_column2):

    return ((df_column1 - df_column2) / df_column2 * 100)   