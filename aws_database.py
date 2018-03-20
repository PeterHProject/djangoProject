#Python project library to read excel, generate create SQL script and update to enter into database. Class also includes create HTML table 
#from data to visualise on website


import psycopg2
import pandas

class PostgresDB:

    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def find_type(self, df):
        type_list = []
        for i in range(0,len(df.iloc[0])):
            if 'int64' in str(type(df.iloc[0][i])):
                sql_query = 'INTEGER'
            elif 'float64' in str(type(df.iloc[0][i])):
                sql_query = 'REAL'
            elif 'str' in str(type(df.iloc[0][i])):
                sql_query = 'TEXT'
            else:
                sql_query = 'OTHER'
            type_list.append(sql_query)
        return type_list

    def find_name(self, df):
        type_name = []
        for i in range(0,len(df.keys())):
            key = df.keys()[i]
            type_name.append(key)
        return type_name

    def create_sql_query(self,df,table_name):
        sql = list()
        sql.append("CREATE TABLE %s " %table_name)
        sql.append("(id INTEGER PRIMARY KEY,")
        list_of_names = self.find_name(df)
        list_of_types = self.find_type(df)
        for a,b in zip(list_of_names[:-1:], list_of_types[:-1:]):
            sql.append(" " + str(a) + " " + str(b) + ",")
        sql.append("%s %s" %(list_of_names[-1], list_of_types[-1]))
        sql.append(")")

        return "".join(sql)

    def create_sql_query_no_id(self,df,table_name):
        sql = list()
        sql.append("CREATE TABLE %s" %table_name)
        sql.append("(")
        list_of_names = self.find_name(df)
        list_of_types = self.find_type(df)
        for a,b in zip(list_of_names[:-1:], list_of_types[:-1:]):
            sql.append("" + str(a) + " " + str(b) + ",")
        sql.append(" %s %s" %(list_of_names[-1], list_of_types[-1]))
        sql.append(")")

        return "".join(sql)


    def execute_create_sql(self, df, table_name):
        sql = self.create_sql_query_no_id(df, table_name)
        conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        cur = conn.cursor()
        cur.execute(sql)
        cur.close()
        conn.commit()

    def execute_general_query(self, sql):
        conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        conn.commit()
        return data

    def connect(self):
        conn = None
        try:
            conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
            cur = conn.cursor()
            print('Postgresdatabase version:')
            cur.execute('SELECT version()')
            db_version = cur.fetchone()
            print(db_version)
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                print('connection closed')

    def insert_into_sql(self, df, table_name):
        sql = list()
        sql.append("INSERT INTO %s" %table_name)
        sql.append("(")
        type_name = self.find_name(df)
        for i in type_name[:-1:]:
            sql.append(i + ",")
        sql.append(type_name[-1] + ") VALUES(")
        for i in type_name[:-1:]:
            sql.append("%s,")
        sql.append("%s)")
        return "".join(sql)

    def create_tuple_from_df(self, df):

        df_tuple = []
        df_list = df_list = df.values.tolist()
        for i in range(0,len(df_list)):
            tuple_list = tuple(df_list[i])
            df_tuple.append(tuple_list)
        return df_tuple

    def execute_insert_many(self, df, table_name):
        conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        cur = conn.cursor()
        sql = self.insert_into_sql(df, table_name)
        data = self.create_tuple_from_df(df)
        cur.executemany(sql, data)
        cur.close()
        conn.commit()

    def df_create_update_database(self, df, table_name):
        #create the database
        self.execute_create_sql(df, table_name)
        #insert into db
        self.execute_insert_many(df, table_name)

    def drop_table_sql(self, table_name):
        sql = "DROP TABLE %s" %table_name
        return sql

    def execute_drop_table(self, table_name):
        sql = self.drop_table_sql(table_name)
        conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        cur = conn.cursor()
        cur.execute(sql)
        cur.close()
        conn.commit()

    def list_all_tables(self):
        sql = "SELECT table_schema,table_name FROM information_schema.tables ORDER BY table_schema,table_name;"
        conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        conn.commit()
        data = [i[1] for i in data if 'public' in i]
        return data

    def show_all_data_in_html(self, table_name):
        sql = "SELECT * FROM %s" %table_name
        conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        cur = conn.cursor()
        cur.execute(sql)
        df_sql = pandas.read_sql_query(sql, conn)
        cur.close()
        conn.commit()
        return df_sql.to_html()

    def show_all_data(self, table_name):
        sql = "SELECT * FROM %s" %table_name
        conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        conn.commit()
        return data

    def run_mappping_query(self, data_table, mapping_table, fx_table):
        sql = list()
        sql.append("SELECT {}.nominal, {}.amount, {}.currency, {}.class_id_1, {}.class_id_2, ".format(data_table,data_table,data_table,data_table,data_table))
        sql.append("{}.class, ".format(mapping_table))
        sql.append("{}.av_fx_rate ".format(fx_table))
        sql.append("FROM ")
        sql.append("{} ".format(data_table))
        sql.append("LEFT JOIN {} ON {}.currency = {}.currency ".format(fx_table,data_table, fx_table))
        sql.append("LEFT JOIN {} ON {}.class_id_1 = {}.mapping_1".format(mapping_table, data_table, mapping_table))
        sql_query =  "".join(sql)
        conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        cur = conn.cursor()
        cur.execute(sql_query)
        df_sql = pandas.read_sql_query(sql_query,conn)
        # data = cur.fetchall()
        # colnames = [desc[0] for desc in cur.description]
        cur.close()
        conn.commit()
        return df_sql.to_html()

    def run_mappping_query_graph(self, data_table, mapping_table, fx_table):
        sql = list()
        sql.append("SELECT {}.nominal, {}.amount, {}.currency, {}.class_id_1, {}.class_id_2, ".format(data_table,data_table,data_table,data_table,data_table))
        sql.append("{}.class, ".format(mapping_table))
        sql.append("{}.av_fx_rate ".format(fx_table))
        sql.append("FROM ")
        sql.append("{} ".format(data_table))
        sql.append("LEFT JOIN {} ON {}.currency = {}.currency ".format(fx_table,data_table, fx_table))
        sql.append("LEFT JOIN {} ON {}.class_id_1 = {}.mapping_1".format(mapping_table, data_table, mapping_table))
        sql_query =  "".join(sql)
        conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        cur = conn.cursor()
        cur.execute(sql_query)
        df_sql = pandas.read_sql_query(sql_query,conn)
        # data = cur.fetchall()
        # colnames = [desc[0] for desc in cur.description]
        cur.close()
        conn.commit()
        return df_sql

    def update_fx_table_sql(self, table_name, key_change, key, new_value, header):
        sql = list()
        sql.append("UPDATE {} ".format(table_name))
        sql.append("SET {} = {} ".format(key, new_value))
        sql.append("WHERE {} = '{}'".format( header, key_change))
        sql_query = "".join(sql)
        conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        cur = conn.cursor()
        cur.execute(sql_query)
        cur.close()
        conn.commit()

    def get_plain_data(self, table_name):
        sql = "SELECT * FROM %s" %table_name
        conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        headers = cur.description
        headers = [i[0] for i in headers]
        info = {}
        info['headers'] = headers
        info['data'] = data
        cur.close()
        conn.commit()
        return info

    def data_to_html_table_edit(self, table_name):
        info = self.get_plain_data(table_name)
        table_html = list()
        table_html.append("""<table class="table"><tr>""")
        for key in info['headers']:
            html = "<th>{}</th>".format(key)
            table_html.append(html)
        table_html.append("</tr>")
        for i in range(0,len(info['data'])):
            table_html.append("<tr>")
            for y in range(0,len(info['headers'])-1):
                table_html.append("<td>{}</td>".format(info['data'][i][y]))
            table_html.append("""<td><input type="text" name="{}" value="{}"></td>""".format(info['data'][i][0],info['data'][i][-1]))
            table_html.append("</tr>")
        table_html.append("</table>")

        return "".join(table_html)

    def data_to_html_table(self, table_name):
        info = self.get_plain_data(table_name)
        table_html = list()
        table_html.append("""<table class="table"><tr>""")
        for key in info['headers']:
            html = "<th>{}</th>".format(key)
            table_html.append(html)
        table_html.append("</tr>")
        for i in range(0,len(info['data'])):
            table_html.append("<tr>")
            for y in range(0,len(info['headers'])):
                table_html.append("<td>{}</td>".format(info['data'][i][y]))
            table_html.append("</tr>")
        table_html.append("</table>")

        return "".join(table_html)


    def data_to_html(self, sql_function_data):
        info = sql_function_data
        table_html = list()
        table_html.append("""<table class="table"><tr>""")
        for key in info['headers']:
            html = "<th>{}</th>".format(key)
            table_html.append(html)
        table_html.append("</tr>")
        for i in range(0,len(info['data'])):
            table_html.append("<tr>")
            for y in range(0,len(info['headers'])):
                table_html.append("<td>{}</td>".format(info['data'][i][y]))
            table_html.append("</tr>")
        table_html.append("</table>")

        return "".join(table_html)

    def run_mappping_query_fetchall(self, data_table, mapping_table, fx_table):
        sql = list()
        sql.append("SELECT {}.nominal, {}.amount, {}.currency, {}.class_id_1, {}.class_id_2, ".format(data_table,data_table,data_table,data_table,data_table))
        sql.append("{}.class, ".format(mapping_table))
        sql.append("{}.av_fx_rate ".format(fx_table))
        sql.append("FROM ")
        sql.append("{} ".format(data_table))
        sql.append("LEFT JOIN {} ON {}.currency = {}.currency ".format(fx_table,data_table, fx_table))
        sql.append("LEFT JOIN {} ON {}.class_id_1 = {}.mapping_1".format(mapping_table, data_table, mapping_table))
        sql_query =  "".join(sql)
        conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        cur = conn.cursor()
        cur.execute(sql_query)
        data = cur.fetchall()
        cur.close()
        conn.commit()
        return data

    def data_to_html_table_editFSOnly(self, table_name):
        info = self.get_plain_data(table_name)
        table_html = list()
        table_html.append("""<table class="table"><tr>""")
        for key in info['headers']:
            html = "<th>{}</th>".format(key)
            table_html.append(html)
        table_html.append("</tr>")
        for i in range(0,len(info['data'])):
            htmlID = info['data'][i][0] + "-"
            table_html.append("<tr>")
            table_html.append("<td>{}</td>".format(info['data'][i][0]))
            table_html.append("""<td><input class="tagDoc" onmouseover="getid(this)" onmouseout="outmouse(this)" id={} type="text" name="{}" value="{}"></td>""".format(htmlID+str(16) ,info['data'][i][1],info['data'][i][1]))
            table_html.append("""<td><input class="tagDoc" id={} onmouseover="getid(this)" onmouseout="outmouse(this)" type="text" name="{}" value="{}"></td>""".format(htmlID+str(17) ,info['data'][i][2],info['data'][i][2]))
            table_html.append("</tr>")
        table_html.append("</table>")

        return "".join(table_html)





# class AwsDatabase:
#     def __init__(self, host, database, user, password):
#         self.host = host
#         self.database = database
#         self.user = user
#         self.password = password
#
#     def connect(self):
#         conn = None
#         try:
#             conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
#             cur = conn.cursor()
#             print('Postgresdatabase version:')
#             cur.execute('SELECT version()')
#             db_version = cur.fetchone()
#             print(db_version)
#             cur.close()
#         except (Exception, psycopg2.DatabaseError) as error:
#             print(error)
#         finally:
#             if conn is not None:
#                 conn.close()
#                 print('connection closed')
#
#     def run_query(self, sql_query):
#
#         sql_query = str(sql_query)
#         conn = None
#         try:
#             # read the connection parameters
#             # connect to the PostgreSQL server
#             conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
#             cur = conn.cursor()
#             # create table one by one
#
#             cur.execute(sql_query)
#             # close communication with the PostgreSQL database server
#             cur.close()
#             # commit the changes
#             conn.commit()
#         except (Exception, psycopg2.DatabaseError) as error:
#             print(error)
#         finally:
#             if conn is not None:
#                 conn.close()
#
#     def upload_spreadsheet(self, df, sql_create_query):
#         conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
#         cur = conn.cursor()
#         SQL = sql_create_query
#         for i in range(0,len(df)):
#             item1 = int(df.iloc[i]['col1'])
#             item2 = int(df.iloc[i]['col2'])
#             cur.execute(SQL, (item1,item2))
#         conn.commit()
#
#     def aws_database_download(self, sql_query):
#         conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
#         cur = conn.cursor()
#         SQL = sql_query
#         cur.execute(SQL)
#         return cur.fetchall()
