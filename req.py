import logging
from bot import hr_data
import psycopg2
import requests

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Request to db
def insert_chat_data(data, phone=False, ries=False):
    try:
        connection = hr_data.conn
        cursor = connection.cursor()
        username = str(data.from_user.username)
        user_id = str(data.from_user.id)
        date = str(data.date)
        text = str(data.text)
        chat_id = str(data.chat.id)
        if phone and ries:
            phone_str = str(phone)
            ries_str = str(ries)
            logger.info("Insert data in db - %s, %s, %s, %s, %s, %s", phone, username, user_id, date, text, chat_id)
            postgres_insert_query = """INSERT INTO hrdata (phone,username,userid,date,text,chatid,ries) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            record_to_insert = (phone_str, username, user_id, date, text, chat_id, ries_str)
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
        else:
            logger.info("Insert data in db - %s, %s, %s, %s, %s, %s", phone, username, user_id, date, text, chat_id)
            postgres_insert_query = """INSERT INTO hrdata (username,userid,date,text,chatid) VALUES (%s, %s, %s, %s, %s)"""
            record_to_insert = (username, user_id, date, text, chat_id)
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
        return True
    except (Exception, psycopg2.Error) as error:
        if connection:
            logger.info("Failed to insert record into mobile table", error)
            return False
    finally:
        if connection:
            print("PostgreSQL connection is closed")


# Request to db
def insert_chatid(data):
    try:
        connection = hr_data.conn
        cursor = connection.cursor()
        chat_id = str(data.chat.id)
        postgres_insert_query = """INSERT INTO hrstate (chatid) VALUES (%s)"""
        cursor.execute(postgres_insert_query, (chat_id,))
        connection.commit()
        return True
    except (Exception, psycopg2.Error) as error:
        if connection:
            logger.info("Failed to insert record into mobile table", error)
            return False
    finally:
        if connection:
            print("PostgreSQL connection is closed")


# Request to db
def select_chatid(data):
    try:
        connection = hr_data.conn
        cursor = connection.cursor()
        chat_id = str(data.chat.id)
        postgres_insert_query = """SELECT chatid FROM hrstate WHERE chatid = %s"""
        cursor.execute(postgres_insert_query, (chat_id,))
        record = cursor.fetchone()
        logger.info(f"chatid - {chat_id}")
        return record
    except (Exception, psycopg2.Error) as error:
        if connection:
            logger.info("Failed to insert record into mobile table", error)
            return False
    finally:
        if connection:
            print("PostgreSQL connection is closed")


# Request to db
def delete_chatid(data):
    try:
        connection = hr_data.conn
        cursor = connection.cursor()
        chat_id = str(data.chat.id)
        postgres_insert_query = """DELETE FROM hrstate WHERE chatid = %s"""
        cursor.execute(postgres_insert_query, (chat_id,))
        connection.commit()
        logger.info(f"Delete chatid - {chat_id}")
        return True
    except (Exception, psycopg2.Error) as error:
        if connection:
            logger.info("Failed to insert record into mobile table", error)
            return False
    finally:
        # closing database connection.
        if connection:
            # connection.close()
            print("PostgreSQL connection is closed")


# Request to Oauth
def ries_oauth():
    url = 'https://oauth2.esoft.tech/token'
    headers = {'Authorization': hr_data.ries['token']}
    data = {
        'grant_type': 'password',
        'username': hr_data.ries['login'],
        'password': hr_data.ries['password']
    }
    response = requests.post(url, headers=headers, data=data)
    json = response.json()
    if response.status_code == 200:
        logger.info(str(json))
        return response
    else:
        logger.info(str(json))
        return False


# Request to Oauth
def auth_handle(data):
    url = 'https://ecosystem.etagi.com/auth/handle'
    json_data = data.json()
    params = {
        'accessToken': json_data['access_token'],
        'refreshToken': json_data['refresh_token'],
        'noredirect': True
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        logger.info(response.text)
        return response
    else:
        logger.info(response.text)
        return False


# Request to Mars - getCandidateTicketsList
def candidate_tickets(data, ries, phone):
    url = 'https://ecosystem.etagi.com/api'
    json_data = data.json()
    session_id = json_data['sessionId']
    body = "{\"filter\": {\"phoneNumber\": " + phone + ", \"responsible\": [" + ries + "]},\"options\": {\"limit\": 10,\"offset\": 0,\"orderBy\": {\"field\": \"createdAt\",\"predicate\": 1}}}"
    data = {
        "service": "hr-business",
        "method": "getCandidateTicketList",
        "body": body,
        "params": "{}"
    }
    headers = {"ECO_SID": session_id}
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        logger.info(response.text)
        return response
    else:
        logger.info(response.text)
        return False


# Request to Mars - createComment
def create_comment(session, id, comment):
    url = 'https://ecosystem.etagi.com/api'
    comment_str = str(comment).replace('\n', " ")
    body = "{\"topic\": 35,\"topicId\": " + id + ",\"comment\": \"" + comment_str + "\"}"
    data = {
        "service": "comments-business",
        "method": "createComment",
        "body": body,
        "params": "{}"
    }
    headers = {"ECO_SID": session}
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        logger.info(response.text)
        return response
    else:
        logger.info(response.text)
        return False


# Request to RIES
def ries_api(data):
    url = 'http://developers.etagi.com/api/v1/staff/list?api_key=' + hr_data.ries['api_key'] + '&filter={"id":"' + data + '"}&select=["id", "fio"]'
    response = requests.get(url)
    logger.info(response)
    return response