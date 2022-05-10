import sqlite3
from unittest import result


class RecordAlarm:
    def __init__(self):
        self.respond = {}
        self.conn = sqlite3.connect('main.db')
        self.cursor = self.conn.cursor()
        check = self.cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='db';")
    
        if check.fetchone()[0] == 0:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS db("
                                    "id TEXT,"
                                    "request_scan BOOLEAN DEFAULT(FALSE),"
                                    "request_capture BOOLEAN DEFAULT(FALSE),"
                                    "request_train_face BOOLEAN DEFAULT(FALSE),"
                                    "alarm_hour TEXT DEFAULT(00),"
                                    "alarm_minute TEXT DEFAULT(00),"
                                    "alarm_status TEXT DEFAULT(00)"
                                    ")")
            print('Main Table created')
            self.initAlarm()
        print("Init Completed")
        

    def initAlarm(self):
        sql_insert_query = "INSERT INTO  db ('id') VALUES (?)"
        data = ('1')
        self.cursor.execute(sql_insert_query, data)
        self.conn.commit()
        print("Alarm set to defaults")
        self.getAlarm()

    def setHour(self, hour):
        # hour = text2int(command)
        if hour is False:
            print("yanlış gelen saat: ", hour)
            self.respond = {'err': 'söylediğin bir saat değil.tekrar dene'}
            return
        exist = self.conn.execute(
            "select alarm_hour from db where id = ?", (1,)).fetchone()
        try:
            if exist is None:
                self.initAlarm()
                self.setHour(hour)
            else:
                sql_update_query = """Update db set hour = ?  WHERE id = ?"""
                data = (hour, '1')
                self.cursor.execute(sql_update_query, data)
                self.conn.commit()
                print("Hour Updated successfully", hour)
            self.respond = self.getAlarm()
        except:
            self.respond = {'err': 'Hour cannot be updated'}
        return self.respond

    def setMinute(self, min):
        # min = text2int(min)
        exist = self.conn.execute(
            "select alarm_minute from db where id = ?", (1,)).fetchone()
        try:
            if exist is None:
                self.initAlarm()
                self.setMinute(min)
            else:
                sql_update_query = "Update db set alarm_minute = ?, status = ? WHERE id = ?"
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
            "select alarm_status from db where id = ?", (1,)).fetchone()
        if exist:
            sql_update_query = """Update db set alarm_status = ? WHERE id = ?"""
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
            "select alarm_status from db where id = ?", (1,)).fetchone()
        if exist:
            sql_update_query = """Update db set alarm_status = ? WHERE id = ?"""
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
            "SELECT * FROM db WHERE id= ? ", '1')
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
    def enableScan(self):
        exist = self.conn.execute(
            "select request_scan from db where id = ?", (1,)).fetchone()
        if exist:
            sql_update_query = """Update db set request_scan = ? WHERE id = ?"""
            data = ('1', '1')
            self.cursor.execute(sql_update_query, data)
            self.conn.commit()
            print("Scan activated ")
            self.respond = self.getAlarm()
        else:
            self.respond = {'err': 'Scan cannot be activated'}
        return self.respond

if __name__ == "__main__":
    import time
    x = RecordAlarm()
    print("respond: ", x.respond)
    # x.setHour("dokuz")
    # print(x.respond)
    # x.setMinute("yirmi")
    # print(x.respond)
    # x.enableAlarm()
    # print(x.respond)
    # x.disableAlarm()
    # print(x.respond)