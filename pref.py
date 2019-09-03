#!/usr/bin/python3
import sqlite3, json, random, string, os
from pathlib import Path
from datetime import datetime


class preferences:
    form_show_inc = 0
    pid_path = ''
    def __init__(self):
        self.conn = sqlite3.connect(self.__generateConfigPath() +
                                    'VPNConnectGUI.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS conf
             (name text, value text)''')
        self.conn.commit()

    def createPID(self):
        pid = self.__getPID()
        path = self.__generateConfigPath() + 'my.pid'
        file = open(path, "w")
        file.write(pid + "\n")
        file.close()
        self.pid_path = path

    def checkPID(self):
        try: 
            path = self.__generateConfigPath() + 'my.pid'
            file = open(path, "r")
            return file.read()
        except FileNotFoundError as e:
            return ""

    def tempFolder(self):
        return self.__generateConfigPath() + "tmp/"

    def generateTempFileCred(self, user, p):
        path = self.__generateFileName()
        file = open(path, "w")
        file.write(user + "\n")
        file.write(p)
        file.close()
        return path

    def insertProxy(self, ip, port, status):
        # value must be in JSON Format
        value = self.__dumpJSON({'ip': ip, 'port': port, 'enabled': status})
        res = self.__checkNameExists("proxy")
        if (int(res) == 1):
            t = (value, "proxy")
            self.__update(t)
        elif (int(res) == 0):
            t = ("proxy", value)
            self.__insert(t)
        elif (int(res) > 1):
            t = ("proxy", )
            self.__delete(t)
            t = ("proxy", value)
            self.__insert(t)

        self.conn.commit()

    def insertDir(self, dir):
        value = self.__dumpJSON({'dir': dir})
        res = self.__checkNameExists("dir")
        if (int(res) == 1):
            t = (value, "dir")
            self.__update(t)
        elif (int(res) == 0):
            t = ("dir", value)
            self.__insert(t)
        elif (int(res) > 1):
            t = ("dir", )
            self.__delete(t)
            t = ("dir", value)
            self.__insert(t)
        self.conn.commit()

    def insertCred(self, user, p):
        value = self.__dumpJSON({'user': user, 'pass': p})
        res = self.__checkNameExists("cred")
        if (int(res) == 1):
            t = (value, "cred")
            self.__update(t)
        elif (int(res) == 0):
            t = ("cred", value)
            self.__insert(t)
        elif (int(res) > 1):
            t = ("cred", )
            self.__delete(t)
            t = ("cred", value)
            self.__insert(t)
        self.conn.commit()

    def getProxy(self):
        t = ("proxy", )
        selectResult = self.__select(t)
        if (str(selectResult) == "None"):
            return ["", "", ""]
        else:
            res = self.__loadJSON(selectResult[1])
            return [res['port'], res['ip'], res['enabled']]

    def getCred(self):
        t = ("cred", )
        selectResult = self.__select(t)
        if (str(selectResult) == "None"):
            return ["", ""]
        else:
            res = self.__loadJSON(selectResult[1])
            return [res['user'], res['pass']]

    def getDirectory(self):
        t = ("dir", )
        selectResult = self.__select(t)
        if (str(selectResult) == "None"):
            return [""]
        else:
            res = self.__loadJSON(selectResult[1])
            return [res['dir']]

    def close(self):
        if self.conn:
            self.conn.close()
    def __getPID(self): 
        return str(os.getpid())

    def __select(self, t):
        self.c.execute('SELECT * FROM conf WHERE name=?', t)
        return self.c.fetchone()

    def __delete(self, t):
        self.c.execute("DELETE FROM conf WHERE name =  ?", t)

    def __update(self, t):
        self.c.execute("UPDATE conf SET value = ? WHERE name = ?", t)

    def __insert(self, t):
        self.c.execute("INSERT INTO conf VALUES (?, ? )", t)

    def __checkNameExists(self, name):
        t = (name, )
        self.c.execute('SELECT COUNT(*) FROM conf WHERE name=?', t)
        r = self.c.fetchone()
        res = str(r[0])
        return res

    def __dumpJSON(self, data):
        return json.dumps(
            data, sort_keys=True, indent=4, separators=(',', ': '))

    def __loadJSON(self, data):
        return json.loads(data)

    def __generateConfigPath(self):
        path = str(Path.home()) + "/.config/VPNConnectGUI/"
        self.__createFolder(path)
        return path

    def __generateFileName(self):
        config = self.tempFolder()
        self.__createFolder(config)
        ran = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for x in range(32))
        return config + ran + str(datetime.now().date()) + "_" + str(
            datetime.now().time()) + ".txt"

    def __createFolder(self, path):
        try:
            os.mkdir(path)
        except OSError as args:
            print("Creation of the directory %s failed. " % path,
                  args.strerror)
        else:
            print("Successfully created the directory %s " % path)
