import pandas as pd
import sqlite3 as db
import datetime as dt

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = db.connect(db_path, check_same_thread=False)

    def execute_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    
class Tables:
    def __init__(self, database):
        self.database = database

    def fetch_list(self):
        query = """SELECT name FROM sqlite_master
            WHERE type='table';"""
        list = self.database.execute_query(query)
        list.remove(('developercrossreference',))
        return list


class Table:
    def __init__(self, name, database):
        self.name = name
        self.database = database

    def fetch_all(self):
        self.all_tables = pd.DataFrame()
        for n in self.name:
            query = f'SELECT * FROM {n}'
            result = self.database.execute_query(query)
            data = [list(row) for row in result]
            columns = ['Index', 'ReceivingCommittee', 'FilingPeriod', 'ContributionDate', 'ContributorName', 'ContributorAddress',\
                    'ContributorType', 'ContributionType', 'ContributionAmount', 'EmployerName', 'EmployerOccupation', 'Office',\
                        'FundType', 'CandidateName', 'CouncilmanicDistrict']
            df = pd.DataFrame(data, columns=columns).drop(columns='Index')
            df.ContributionDate = pd.to_datetime(df.ContributionDate)
            df.ContributionDate = df.ContributionDate.dt.date
            self.all_tables = pd.concat([self.all_tables, df], ignore_index=True)
        return self.all_tables
    
    def fetch_reference(self):
        query = f"SELECT * FROM {self.name}"
        result = self.database.execute_query(query)
        data = [list(row) for row in result]
        columns = ['Index','ContributorName', 'DeveloperOrDeveloperAffiliated']
        return pd.DataFrame(data, columns=columns).drop(columns='Index')