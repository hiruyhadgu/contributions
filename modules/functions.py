import pandas as pd


def group_by_filing_period(table, args):

    group_by_filing_period = table.set_index(args).groupby(level=[i for i in range(len(args))]).sum(numeric_only=True)

    return group_by_filing_period

def summary_tables(table, *args):
    summary_table = group_by_filing_period(table, *args)
    summary_table = summary_table.unstack()
    summary_table.columns = summary_table.columns.droplevel(0)
    return summary_table