#helper functions
#pip3 freeze > requirements.txt 

"""
Calculates the percent change of a column in a dataframe
"""
def pct_change(df_column):

    return ((df_column - df_column.shift(1)) / df_column.shift(1) * 100)

"""
Calculates the percent change with two column in a dataframe
"""

def pct_change_c1_c2(df_column1, df_column2):

    return ((df_column1 - df_column2) / df_column2 * 100)   













