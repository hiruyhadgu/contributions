import pandas as pd


def group_by_filing_period(table, args):

    group_by_filing_period = table.set_index(args).groupby(level=[i for i in range(len(args))]).sum(numeric_only=True)

    return group_by_filing_period