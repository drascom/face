import sqlite3
from unittest import result
from utils import text2int


class RecordAlarm:
    def __init__(self):
        self.respond = {}
        self.conn = sqlite3.connect('main.db')
        self.cursor = self.conn.cursor()

        # self.cursor.execute(''' SELECT count(*) FROM sqlite_master WHERE type='table' AND name='user' ''')
        # first_table = next(self.cursor, [None])[0]
        # if first_table ==0:
        #     self.cursor.execute("CREATE TABLE user (name TEXT, lang TEXT)")

        self.cursor.execute(
            ''' SELECT count(*) FROM sqlite_master WHERE type='table' AND name='alarm' ''')
        second_table = next(self.cursor, [None])[0]
        if second_table == 0:
            self.cursor.execute(
                "CREATE TABLE alarm (id TEXT, hour TEXT, min TEXT, status TEXT)")
            print('Alarm Table created')
            self.initAlarm()
            print('Record inserted successfully')
        self.getAlarm()

    def initAlarm(self):
        print("Alarm init fired")
        sql_insert_query = "INSERT INTO  alarm ('id','hour','min','status') VALUES (?,?,?,?)"
        data = ('1', '08', '00', 'off')
        self.cursor.execute(sql_insert_query, data)
        self.conn.commit()
        self.getAlarm()

    def setHour(self, command):
        hour = text2int(command)
        if hour is False:
            print("yanlış gelen saat: ", command)
            self.respond = {'err': 'söylediğin bir saat değil.tekrar dene'}
            return
        exist = self.conn.execute(
            "select hour from alarm where id = ?", (1,)).fetchone()
        try:
            if exist is None:
                self.initAlarm()
                self.setHour(hour)
            else:
                sql_update_query = """Update alarm set hour = ?  WHERE id = ?"""
                data = (hour, '1')
                self.cursor.execute(sql_update_query, data)
                self.conn.commit()
                print("Hour Updated successfully", hour)
            self.respond = self.getAlarm()
        except:
            self.respond = {'err': 'Hour cannot be updated'}
        return self.respond

    def setMinute(self, min):
        min = text2int(min)
        exist = self.conn.execute(
            "select min from alarm where id = ?", (1,)).fetchone()
        try:
            if exist is None:
                self.initAlarm()
                self.setMinute(min)
            else:
                sql_update_query = "Update alarm set min = ?, status = ? WHERE id = ?"
                data = (min, 'on', '1')
                self.cursor.execute(sql_update_query, data)
                self.conn.commit()
                print("Minute Updated successfully", min)
            self.respond = self.getAlarm()
        except:
            self.respond = {'err': 'Minute cannot be updated'}
        return self.respond

    def disableAlarm(self):
        exist = self.conn.execute(
            "select status from alarm where id = ?", (1,)).fetchone()
        if exist:
            sql_update_query = """Update alarm set status = ? WHERE id = ?"""
            data = ('off', '1')
            self.cursor.execute(sql_update_query, data)
            self.conn.commit()
            print("Alarm disabled successfully")
            self.respond = self.getAlarm()
        else:
            self.respond = {'err': 'Minute cannot be updated'}
        return self.respond

    def enableAlarm(self):
        exist = self.conn.execute(
            "select status from alarm where id = ?", (1,)).fetchone()
        if exist:
            sql_update_query = """Update alarm set status = ? WHERE id = ?"""
            data = ('on', '1')
            self.cursor.execute(sql_update_query, data)
            self.conn.commit()
            print("Alarm activated successfully")
            self.respond = self.getAlarm()
        else:
            self.respond = {'err': 'Minute cannot be updated'}
        return self.respond

    def getAlarm(self):
        output_obj = self.cursor.execute(
            "SELECT * FROM alarm WHERE id= ? ", '1')
        results = output_obj.fetchall()
        # for row in results:
        #     row_as_dict = {output_obj.description[i][0]:row[i] for i in range(len(row))}
        row_as_dict = {
            output_obj.description[i][0]: results[0][i] for i in range(len(results[0]))
        }
        if row_as_dict:
            self.respond = row_as_dict
            return row_as_dict
        else:
            return {'err': 'Alarm record not found'}


if __name__ == "__main__":
    import time
    x = RecordAlarm()
    print("respond: ", x.respond)
    x.setHour("dokuz")
    print(x.respond)
    x.setMinute("yirmi")
    print(x.respond)
    x.enableAlarm()
    print(x.respond)
    x.disableAlarm()
    print(x.respond)
