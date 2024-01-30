import sqlite3

from Reflection.encryption import symmetrical_encryption


class Db:
    def __init__(self):
        self.db_name = "reflection_db"
        self.conn = None
        self.curr = None
        self.users_tbl = "user_pass"
        self.mac_tbl = "user_mac"
        self.encryption = symmetrical_encryption.SymmetricalEncryption()
        self._create_db()

    def _create_db(self):
        """
        connect to DB and create tables if they do not exist
        :return:
        """
        self.conn = sqlite3.connect(self.db_name)
        self.curr = self.conn.cursor()
        sql = ["CREATE TABLE IF NOT EXISTS " + self.users_tbl +
               "(user VARCHAR(30), password VARCHAR(30), PRIMARY KEY(user))",
               "CREATE TABLE IF NOT EXISTS " + self.mac_tbl +
               "(user VARCHAR(30), mac VARCHAR(17), PRIMARY KEY(user, mac))"]

        [self.curr.execute(s) for s in sql]
        self.conn.commit()

    def _username_exists(self, username: str) -> bool:
        """
        check if username exists in the user_pass table
        :param username: username
        :return: boolean
        """
        sql = "SELECT user FROM " + self.users_tbl + " WHERE user = ?"
        self.curr.execute(sql, (username,))
        return self.curr.fetchone() is not None

    def _username_mac_exists(self, username: str, mac: str) -> bool:
        """
        check if username and mac together exists in the user_mac table
        :param username: username
        :param mac: mac address
        :return: boolean
        """
        sql = "SELECT user FROM " + self.mac_tbl + " WHERE user = ? and mac = ?"
        self.curr.execute(sql, (username, mac,))
        return self.curr.fetchone() is not None


    def add_user(self, username: str, password: str) -> bool:
        """
        adds user to user_pass table
        :param username: username
        :param password: password
        :return: True or False
        """
        flag = True
        if self._username_exists(username):
            flag = False
        else:
            print(self.users_tbl)
            sql = "INSERT INTO " + self.users_tbl + " VALUES(?,?)"
            self.curr.execute(sql, (username, self.encryption.hash(password),))
            self.conn.commit()

        return flag


    def add_user_mac(self, username: str, mac: str) -> bool:
        """
        adds user to user_pass table
        :param username: username
        :param mac: mac address
        :return: True or False
        """
        flag = True
        if self._username_mac_exists(username, mac):
            flag = False
        else:
            sql = "INSERT INTO " + self.mac_tbl + " VALUES(?,?)"
            self.curr.execute(sql, (username, mac,))
            self.conn.commit()

        return flag


    def change_password(self, username: str, password: str):
        """
        changing password of username and returns a boolean
        :param username: username
        :param password: password
        :return: a boolean
        """
        flag = True
        if not self._username_exists(username):
            flag = False

        else:
            sql = "UPDATE " + self.users_tbl\
                  + " SET password = ? WHERE user = ?"
            self.curr.execute(sql, (self.encryption.hash(password), username))
            self.conn.commit()
        return flag


    def get_password(self, username: str):
        """
        return the password of a username if exists
        :param username: username
        :return: password or None
        """
        if self._username_exists(username):
            sql = "SELECT password FROM " + self.users_tbl + " WHERE user = ?"
            self.curr.execute(sql, (username,))
            password = self.curr.fetchone()[0]
            return password

    def get_macs(self, username):
        """
        gets username and returns a list of all macs related to that user
        :param username: username
        :return: a list of all macs related to user
        """
        sql = "SELECT mac FROM " + self.mac_tbl + " WHERE user = ?"
        self.curr.execute(sql, (username,))
        macs = self.curr.fetchall()
        return [row[0] for row in macs]


    def get_users(self, mac):
        """
        gets username and returns a list of all macs related to that user
        :param mac: mac address
        :return: a list of all macs related to user
        """
        sql = "SELECT user FROM " + self.mac_tbl + " WHERE mac = ?"
        self.curr.execute(sql, (mac,))
        users = self.curr.fetchall()
        return [row[0] for row in users]


if __name__ == '__main__':
    db = Db()
    print(db.add_user('yotam_king', '1234'))
    print(db.get_users('mac8'))
