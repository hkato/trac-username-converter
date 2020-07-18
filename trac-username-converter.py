#!/usr/bin/env python
#
# Trac username converter
#   This script only tested on
#       - trac.db system.database_version = 29 (Trac 1.0.3)
#       - Python 3.8.3
#

#
# The MIT License (MIT)
#
# Copyright (c) 2020 Hideyuki KATO
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import argparse
import csv
import pathlib
import sqlite3

TRAC_DB_PATH='db/trac.db'
USERMAP_FILE='usermap.csv'

SQL_GET_TRAC_USERS = """
CREATE TABLE temp.users(username TEXT);
INSERT INTO temp.users(username) SELECT DISTINCT author FROM attachment;
INSERT INTO temp.users(username) SELECT DISTINCT owner FROM component;
INSERT INTO temp.users(username) SELECT DISTINCT username FROM permission;
INSERT INTO temp.users(username) SELECT DISTINCT author FROM revision;
INSERT INTO temp.users(username) SELECT DISTINCT owner FROM ticket WHERE owner IS NOT NULL; 
INSERT INTO temp.users(username) SELECT DISTINCT reporter FROM ticket;
INSERT INTO temp.users(username) SELECT DISTINCT cc FROM ticket WHERE cc IS NOT NULL;
INSERT INTO temp.users(username) SELECT DISTINCT author FROM ticket_change;
INSERT INTO temp.users(username) SELECT DISTINCT author FROM wiki;
"""


class TracUsernameConverter():

    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(self.path + '/' + TRAC_DB_PATH)
        self.export_file = pathlib.Path(path).name + '-' + USERMAP_FILE

    def export_trac_users(self):
        print('Export Trac user list... ' + self.export_file)
        cursor = self.conn.cursor()
        cursor.executescript(SQL_GET_TRAC_USERS)
        trac_users = cursor.execute(
            "SELECT DISTINCT username, NULL FROM temp.users WHERE username IS NOT NULL AND username <> '' ORDER BY username ASC;")
        with open(self.export_file, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['old', 'new'])
            writer.writerows(trac_users)

    def create_usermap(self):
        print('Please edit this file: ' + self.export_file)

    def import_usermap(self):
        cursor = self.conn.cursor()
        cursor.execute('CREATE TABLE temp.usermap(old TEXT, new TEXT);')
        with open(self.export_file, 'r') as f:
            csv_data = csv.reader(f)
            header = next(csv_data)
            for row in csv_data:
                cursor.execute('INSERT INTO usermap VALUES (?,?);', row)

    def update_trac_users(self):
        cursor = self.conn.cursor()
        usermap = cursor.execute("SELECT * FROM usermap").fetchall()
        for user in usermap:
            user_old = user[0]
            user_new = user[1]
            to_from = (user_new, user_old)
            print('Converting... ' + user_old + ' -> ' + user_new)
            cursor.execute('UPDATE attachment SET author=? WHERE author=?;', to_from)
            cursor.execute('UPDATE revision SET author=? WHERE author=?;', to_from)
            cursor.execute('UPDATE ticket_change SET author=? WHERE author=?;', to_from)
            cursor.execute('UPDATE permission SET username=? WHERE username=?;', to_from)
            cursor.execute('UPDATE component SET owner=? WHERE owner=?;', to_from)
            cursor.execute('UPDATE wiki SET author=? WHERE author=?;', to_from)
            cursor.execute('UPDATE ticket SET owner=? WHERE owner=?;', to_from)
            cursor.execute('UPDATE ticket SET reporter=? WHERE reporter=?;', to_from)
            cursor.execute('UPDATE ticket SET reporter=? WHERE reporter=?;', to_from)
            cursor.execute('UPDATE ticket SET cc=? WHERE cc=?;', to_from)

        self.conn.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='[ export | convert ]')
    parser.add_argument('path', help='Trac project path')

    args = parser.parse_args()

    user_name_conv = TracUsernameConverter(args.path)

    if (args.action == 'export'):
        user_name_conv.export_trac_users()
        user_name_conv.create_usermap()
    elif (args.action == 'convert'):
        user_name_conv.import_usermap()
        user_name_conv.update_trac_users()
