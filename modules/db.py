import configparser
import logging
import os
from datetime import datetime
from decimal import *

import pymysql

# Set Log File
logging.basicConfig(
    handlers=[
        logging.FileHandler(os.environ['MY_LOG_DIR'] + '/webhooks.log', 'a')
    ],
    level=logging.INFO)

# Read config and parse constants
config = configparser.ConfigParser()
config.read(os.environ['MY_CONF_DIR'] + '/webhooks.ini')

# DB connection settings
DB_HOST = config.get('webhooks', 'host')
DB_USER = config.get('webhooks', 'user')
DB_PW = config.get('webhooks', 'password')
DB_SCHEMA = config.get('webhooks', 'schema')


def check_db_exist():
    db = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PW, port=3307)
    with db:
        sql = "SHOW DATABASES LIKE '{}'".format(DB_SCHEMA)
        db_cursor = db.cursor()
        a = db_cursor.execute(sql)
        return a == 1


def create_db():
    db = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PW, port=3307)
    with db:
        db_cursor = db.cursor()
        sql = 'CREATE DATABASE IF NOT EXISTS {}'.format(DB_SCHEMA)
        db_cursor.execute(sql)
        db.commit()
        print('Created database')


def delete_db():
    try:
        if check_db_exist():
            db = pymysql.connect(
                host=DB_HOST, user=DB_USER, passwd=DB_PW, port=3307)
            with db:
                db_cursor = db.cursor()
                sql = 'DROP DATABASE {}'.format(DB_SCHEMA)
                db_cursor.execute(sql)
        else:
            print('No db')
    except Exception as e:
        print('Failed removing db: {}'.format(e))
    else:
        print('Deleted database.')
    check_db_exist()


def check_table_exists(table_name):
    db = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PW,
        db=DB_SCHEMA,
        port=3307,
        use_unicode=True,
        charset="utf8")
    with db:
        db_cursor = db.cursor()
        stmt = "SHOW TABLES LIKE '{}'".format(table_name)
        db_cursor.execute(stmt)
        result = db_cursor.fetchall()
        return result


def execute_sql(sql):
    db = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PW,
        port=3307,
        db=DB_SCHEMA,
        use_unicode=True,
        charset="utf8")
    with db:
        db_cursor = db.cursor()
        db_cursor.execute(sql)


def create_tables():
    users_exist = check_table_exists('users')
    if not users_exist:
        # create users table
        sql = """
        CREATE TABLE USERS ( 
            USER_ID INT,
            USER_NAME  CHAR(64),
            ACCOUNT CHAR(128),  
            REGISTER SMALLINT)
            """
        execute_sql(sql)
        print("Checking if table was created: {}".format(
            check_table_exists('users')))

    users_exist = check_table_exists('telegram_chat_members')
    if not users_exist:
        # create telegram_chat_members table
        sql = """
        CREATE TABLE IF NOT EXISTS TELEGRAM_CHAT_MEMBERS (
            CHAT_ID INT,
            CHAT_NAME  CHAR(128),
            MEMBER_ID INT,  
            MEMBER_NAME CHAR(128))
            """
        res = execute_sql(sql)

    users_exist = check_table_exists('tip_list')
    if not users_exist:
        # create tip_list table
        sql = """
        CREATE TABLE IF NOT EXISTS TIP_LIST (
            DM_ID INT,
            TX_ID  INT,
            PROCESSED INT,  
            SENDER_ID INT,  
            RECEIVER_ID INT,  
            DM_TEXT CHAR(128),  
            AMOUNT INT,  
            MEMBER_NAME CHAR(64))
            """
        res = execute_sql(sql)


def get_db_data(db_call):
    """
    Retrieve data from DB
    """
    db = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        port=3307,
        passwd=DB_PW,
        db=DB_SCHEMA,
        use_unicode=True,
        charset="utf8")
    with db:
        db_cursor = db.cursor()
        db_cursor.execute(db_call)
        db_data = db_cursor.fetchall()
        return db_data


def set_db_data(db_call):
    """
    Enter data into DB
    """
    db = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PW,
        port=3307,
        db=DB_SCHEMA,
        use_unicode=True,
        charset="utf8")
    try:
        with db:
            db_cursor = db.cursor()
            db_cursor.execute(db_call)
            logging.info("{}: record inserted into DB".format(datetime.now()))
    except pymysql.ProgrammingError as e:
        logging.info("{}: Exception entering data into database".format(
            datetime.now()))
        logging.info("{}: {}".format(datetime.now(), e))
        raise e


def set_db_data_tip(message, users_to_tip, t_index):
    """
    Special case to update DB information to include tip data
    """
    logging.info("{}: inserting tip into DB.".format(datetime.now()))
    db = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PW,
        port=3307,
        db=DB_SCHEMA,
        use_unicode=True,
        charset="utf8")
    try:
        with db:
            db_cursor = db.cursor()
            db_cursor.execute(
                "INSERT INTO tip_list (dm_id, tx_id, processed, sender_id, receiver_id, system, dm_text, amount)"
                " VALUES (%s, %s, 2, %s, %s, %s, %s, %s)",
                (message['id'], message['tip_id'], message['sender_id'],
                 users_to_tip[t_index]['receiver_id'], message['system'],
                 message['text'], Decimal(message['tip_amount'])))
    except Exception as e:
        logging.info("{}: Exception in set_db_data_tip".format(datetime.now()))
        logging.info("{}: {}".format(datetime.now(), e))
        raise e
