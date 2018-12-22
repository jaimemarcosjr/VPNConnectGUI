#!/usr/bin/python3
import sqlite3, json, random, string, os
from pathlib import Path
from datetime import datetime
class preferences:

    def __init__(self):
        self.conn = sqlite3.connect(self.__generateConfigPath() + 'VPNConnectGUI.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS conf
             (name text, value text)''')
        self.conn.commit()
    def deleteTempFile(self, path):
        if os.path.exists(path):
            os.remove(path)
        else:
            print("The file does not exist")

    def generateTempFileCred(self, user, p):
        path = self.__generateFileName()
        file = open( path ,"w" )
        file.write(user + "\n")
        file.write(p)
        file.close()
        return path

    def insertProxy(self, ip, port, status):
        # value must be in JSON Format
        value = self.__dumpJSON({'ip': ip, 'port': port, 'enabled' : status})
        res = self.__checkNameExists("proxy")
        print(res)
        if(int(res) == 1):
            t = (value,"proxy")
            self.__update(t)
        elif(int(res) == 0):
            t = ("proxy",value)
            self.__insert(t)
        elif(int(res) > 1):
            t = ("proxy",)
            self.__delete(t)
            t = ("proxy",value)
            self.__insert(t)

        self.conn.commit()
    def insertDir(self, dir):
        value = self.__dumpJSON({'dir': dir})
        res = self.__checkNameExists("dir")
        print(res)
        if(int(res) == 1):
            t = (value,"dir")
            self.__update(t)
        elif(int(res) == 0):
            t = ("dir",value)
            self.__insert(t)
        elif(int(res) > 1):
            t = ("dir",)
            self.__delete(t)
            t = ("dir",value)
            self.__insert(t)
        self.conn.commit()
    def insertCred(self, user, p):
        value = self.__dumpJSON({'user': user, 'pass': p})
        res = self.__checkNameExists("cred")
        print(res)
        if(int(res) == 1):
            t = (value,"cred")
            self.__update(t)
        elif(int(res) == 0):
            t = ("cred",value)
            self.__insert(t)
        elif(int(res) > 1):
            t = ("cred",)
            self.__delete(t)
            t = ("cred",value)
            self.__insert(t)
        self.conn.commit()
    def getProxy(self):
        t = ("proxy", )
        selectResult = self.__select(t)
        if(str(selectResult) == "None"):
            print("None")
            return ["", "", ""]
        else:
            res = self.__loadJSON(selectResult[1])
            return [res['port'], res['ip'], res['enabled']]
    def getCred(self):
        t = ("cred", )
        selectResult = self.__select(t)
        if(str(selectResult) == "None"):
            print("None")
            return ["", ""]
        else:
            res = self.__loadJSON(selectResult[1])
            return [res['user'], res['pass']]
    def getDirectory(self):
        t = ("dir", )
        selectResult = self.__select(t)
        if(str(selectResult) == "None"):
            print("None")
            return [""]
        else:
            res = self.__loadJSON(selectResult[1])
            return [res['dir']]
    def close(self):
        if self.conn:
            print("Closing database....")
            self.conn.close()

    def __select(self, t):
        self.c.execute('SELECT * FROM conf WHERE name=?', t)
        return self.c.fetchone()

    def __delete(self, t):
        self.c.execute("DELETE FROM conf WHERE name =  ?", t )
        print("")
    def __update(self, t):
        self.c.execute("UPDATE conf SET value = ? WHERE name = ?", t )
        print("update")

    def __insert(self, t):
        self.c.execute("INSERT INTO conf VALUES (?, ? )", t)
        print("insert")

    def __checkNameExists(self, name):
        t = (name,)
        self.c.execute('SELECT COUNT(*) FROM conf WHERE name=?', t)
        r = self.c.fetchone()
        res = str(r[0])
        return res
        
    def __dumpJSON(self, data):
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    def __loadJSON(self, data):
        return json.loads(data)
    def __generateConfigPath(self):
        return str(Path.home()) + "/.config/"
    def __generateFileName(self):
        config = self.__generateConfigPath()
        ran = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
        return config + ran + str(datetime.now().date()) + "_" + str(datetime.now().time()) + ".txt"
