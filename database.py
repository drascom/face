import sqlite3
from unittest import result


class DataRecords:
    def __init__(self):
        self.respond = {}
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        check = cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='db';")
    
        if check.fetchone()[0] == 0:
            cursor.execute("CREATE TABLE IF NOT EXISTS db("
                                    "id TEXT,"
                                    "view_camera NUMERIC DEFAULT(0)"
                                    "request_scan BOOLEAN DEFAULT(FALSE),"
                                    "request_capture BOOLEAN DEFAULT(FALSE),"
                                    "request_train_face BOOLEAN DEFAULT(FALSE),"
                                    "alarm_hour TEXT DEFAULT(00),"
                                    "alarm_minute TEXT DEFAULT(00),"
                                    "alarm_status TEXT DEFAULT(00)"
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

    def setHour(self, hour):
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        # hour = text2int(command)
        if hour is False:
            print("yanlış gelen saat: ", hour)
            self.respond = {'err': 'söylediğin bir saat değil.tekrar dene'}
            return
        exist = conn.execute(
            "select alarm_hour from db where id = ?", (1,)).fetchone()
        try:
            if exist is None:
                self.initAlarm()
                self.setHour(hour)
            else:
                sql_update_query = """Update db set hour = ?  WHERE id = ?"""
                data = (hour, '1')
                cursor.execute(sql_update_query, data)
                conn.commit()
                print("Hour Updated successfully", hour)
            self.respond = self.getData()
        except:
            self.respond = {'err': 'Hour cannot be updated'}
        return self.respond

    def setMinute(self, min):
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        # min = text2int(min)
        exist = conn.execute(
            "select alarm_minute from db where id = ?", (1,)).fetchone()
        try:
            if exist is None:
                self.initAlarm()
                self.setMinute(min)
            else:
                sql_update_query = "Update db set alarm_minute = ?, status = ? WHERE id = ?"
                data = (min, 'on', '1')
                cursor.execute(sql_update_query, data)
                conn.commit()
                print("Minute Updated successfully", min)
            self.respond = self.getData()
        except:
            self.respond = {'err': 'Minute cannot be updated'}
        return self.respond

    def disableAlarm(self):
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        
        exist = conn.execute(
            "select alarm_status from db where id = ?", (1,)).fetchone()
        if exist:
            sql_update_query = """Update db set alarm_status = ? WHERE id = ?"""
            data = ('off', '1')
            cursor.execute(sql_update_query, data)
            conn.commit()
            print("Alarm disabled successfully")
            self.respond = self.getData()
        else:
            self.respond = {'err': 'Minute cannot be updated'}
        return self.respond

    def enableAlarm(self):
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        
        exist = conn.execute(
            "select alarm_status from db where id = ?", (1,)).fetchone()
        if exist:
            sql_update_query = """Update db set alarm_status = ? WHERE id = ?"""
            data = ('on', '1')
            cursor.execute(sql_update_query, data)
            conn.commit()
            print("Alarm activated successfully")
            self.respond = self.getData()
        else:
            self.respond = {'err': 'Minute cannot be updated'}
        return self.respond

    def getData(self):
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        row_as_dict = None
        output_obj = cursor.execute(
            "SELECT * FROM db WHERE id= ? ", '0')
        results = output_obj.fetchall()
        
        for row in results:
            row_as_dict = {output_obj.description[i][0]:row[i] for i in range(len(row))}
        if row_as_dict:
            self.respond = row_as_dict
            return row_as_dict
        else:
            return {'err': 'Data record not found'}
        conn.commit()

        
    def request_scan(self,value):
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        
        exist = cursor.execute(
            "select request_scan from db where id = ?", (0,)).fetchone()
        if exist:
            sql_update_query = """Update db set request_scan = ? WHERE id = ?"""
            data = ('1', '0')
            cursor.execute(sql_update_query, data)
            conn.commit()
            print("Scan activated ")
            self.respond = self.getData()
        else:
            self.respond = {'err': 'Scan cannot be activated'}
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