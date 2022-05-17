import sqlite3
from unittest import result


class DataRecords:
    def __init__(self):
        self.respond = {}
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        check = cursor.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='db';")

        if check.fetchone()[0] == 0:
            cursor.execute("CREATE TABLE IF NOT EXISTS db("
                           "id TEXT,"
                           "section NUMERIC DEFAULT(0),"
                           "request_scan BOOLEAN DEFAULT(FALSE),"
                           "request_capture BOOLEAN DEFAULT(FALSE),"
                           "request_view BOOLEAN DEFAULT(FALSE),"
                           ")")
            print('Main Table created')
            self.initDefaults()

    def initDefaults(self):
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        sql_insert_query = "INSERT INTO  db ('id') VALUES (?)"
        data = ('0')
        cursor.execute(sql_insert_query, data)
        print("Init Completed")
        self.getData()
        conn.commit()

    def getData(self):
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        row_as_dict = None
        output_obj = cursor.execute(
            "SELECT * FROM db WHERE id= ? ", '0')
        results = output_obj.fetchall()

        for row in results:
            row_as_dict = {
                output_obj.description[i][0]: row[i] for i in range(len(row))}
        if row_as_dict:
            self.respond = row_as_dict
            return row_as_dict
        else:
            return {'err': 'Data record not found'}
        conn.commit()

    def getColumn(self,column):
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        row_as_dict = None
        output_obj = cursor.execute(
            "SELECT "+ column +" FROM db WHERE id= ? ", '0')
        results = output_obj.fetchall()

        for row in results:
            row_as_dict = {
                output_obj.description[i][0]: row[i] for i in range(len(row))}
        if row_as_dict:
            self.respond = row_as_dict
            return row_as_dict
        else:
            return {'err': 'Data record not found'}
        conn.commit()


    def request(self, column, value):
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()

        exist = cursor.execute(
            "select request_scan from db where id = ?", (0,)).fetchone()
        if exist:
            sql_update_query = "Update db set "+column + " = ? WHERE id = ?"
            data = (value, '0')
            cursor.execute(sql_update_query, data)
            conn.commit()
            print("DB Gelen Value: ",value)
            status = " activated " if value else " deactivated" 
            print(column + status)
            self.respond = self.getData()
        else:
            self.respond = {'err': column + 'cannot be activated'}
        return self.respond


if __name__ == "__main__":
    import time
    x = DataRecords()
    print("respond: ", x.getData())
    # x.setHour("dokuz")
    # print(x.respond)
    # x.setMinute("yirmi")
    # print(x.respond)
    # x.enableAlarm()
    # print(x.respond)
    # x.disableAlarm()
    # print(x.respond)
