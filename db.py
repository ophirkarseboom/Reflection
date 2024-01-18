import sqlite3


class Db:
    def __init__(self):

        self.db_name = "reflection_db"
        self.conn = None
        self.curr = None
        self.users_tbl = "user_pass"
        self.mac_tbl = "user_mac"
        self._create_db()

    def _create_db(self):
        """
        connect to DB and create tables if they do not exists
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
        sql = "SELECT user FROM " + self.users_tbl + " WHERE user = ? and mac = ?"
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
            self.curr.execute(sql, (username, password,))
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
            print(self.users_tbl)
            sql = "INSERT INTO " + self.users_tbl + " VALUES(?,?)"
            self.curr.execute(sql, (username, mac,))
            self.conn.commit()

        return flag


    def change_password(self, username: str, password: str):
        flag = True
        if not self._username_exists(username):
            flag = False

        else:
            sql = "UPDATE " + self.users_tbl\
                  + " SET password = ? WHERE user = ?"
            self.curr.execute(sql, (username, password,))
            self.conn.commit()
        return flag



    # def get_teacher_name(self, teacher_id: str) -> str:
    #     """
    #     return the name of the teacher if teacher_id exists
    #     :param teacher_id: id number
    #     :return: teacher_name or None
    #     """
    #     if self._teacher_id_exists(teacher_id):
    #         sql = "SELECT name FROM " + self.teachers_table + " WHERE teacher_id = ?"
    #         self.curr.execute(sql, (teacher_id,))
    #         teacher_name, = self.curr.fetchone()
    #         return teacher_name
    #
    # def _student_id_exists(self, student_id: str) -> bool:
    #     """
    #     check if student_id exists in the students table
    #     :param student_id: id number
    #     :return: True or False
    #     """
    #     sql = "SELECT student_id FROM " + self.students_table + " WHERE student_id = ?"
    #     self.curr.execute(sql, (student_id,))
    #     self.curr.execute(sql)
    #     return self.curr.fetchone() is not None
    #
    # def get_student_name(self, student_id: str) -> str:
    #     """
    #     return the name of the student if student_id exists
    #     :param student_id: id number
    #     :return: student_name or None
    #     """
    #     if self._student_id_exists(student_id):
    #         sql = "SELECT name FROM " + self.students_table + " WHERE student_id = ?"
    #         self.curr.execute(sql, (student_id,))
    #         student_name, = self.curr.fetchone()
    #         return student_name
    #
    # def get_student_class(self, student_id: str) -> str:
    #     """
    #     return the class of the student if student_id exists
    #     :param student_id: id number
    #     :return: student_class or None
    #     """
    #     if self._student_id_exists(student_id):
    #         sql = "SELECT class FROM " + self.students_table + " WHERE student_id = ?"
    #         self.curr.execute(sql, (student_id,))
    #         student_class, = self.curr.fetchone()
    #         return student_class
    #
    # def get_student_gender(self, student_id: str) -> str:
    #     """
    #     return the gender of the student if student_id exists
    #     :param student_id: id number
    #     :return: student_gender or None
    #     """
    #     if self._student_id_exists(student_id):
    #         sql = "SELECT gender FROM " + self.students_table + " WHERE student_id = ?"
    #         self.curr.execute(sql, (student_id,))
    #         student_gender, = self.curr.fetchone()
    #         return student_gender
    #
    # def get_teacher_classes(self, teacher_id: str) -> list:
    #     """
    #     return the classes of the teacher if teacher_id exists
    #     :param teacher_id: id number
    #     :return: teacher_classes (list) or None
    #     """
    #     if self._teacher_id_exists(teacher_id):
    #         sql = "SELECT class FROM " + self.classes_table + " WHERE teacher_id = ?"
    #         self.curr.execute(sql, (teacher_id,))
    #         list = self.curr.fetchall()
    #         teacher_classes = []
    #         for c in list:
    #             c, = c
    #             teacher_classes.append(c)
    #         return teacher_classes
    #
    # def _mac_address_exists(self, mac_address: str) -> bool:
    #     """
    #     check if mac_address exists in the computers table
    #     :param mac_address: mac address
    #     :return: True or False
    #     """
    #     sql = "SELECT mac_address FROM " + self.computers_table + " WHERE mac_address = ?"
    #     self.curr.execute(sql, (mac_address,))
    #     return self.curr.fetchone() is not None
    #
    # def get_computer_id(self, mac_address: str) -> str:
    #     """
    #     return the id of the computer if mac_address exists
    #     :param mac_address: mac address
    #     :return: computer_id or None
    #     """
    #     if self._mac_address_exists(mac_address):
    #         sql = "SELECT computer_id FROM " + self.computers_table + " WHERE mac_address = ?"
    #         self.curr.execute(sql, (mac_address,))
    #         computer_id, = self.curr.fetchone()
    #         return computer_id


if __name__ == '__main__':
    db = Db()
    status = db.add_user('ophir', '12345')
    print(db.change_password('ophir', '3333'))
