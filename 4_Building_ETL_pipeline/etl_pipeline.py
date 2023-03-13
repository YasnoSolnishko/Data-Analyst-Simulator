# coding=utf-8

from datetime import datetime, timedelta
import pandas as pd
from io import StringIO
import requests
from datetime import date
import pandahouse as ph

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.macros import ds_add


# Get data from clickhouse

def ch_get_data(query='Select 1',
              host='https://clickhouse.lab.karpov.courses',
              user='student',
              password='dpo_python_2020'):
    r = requests.post(host,
                      data=query.encode("utf-8"),
                      auth=(user, password),
                      verify=False)
    result = pd.read_csv(StringIO(r.text), sep='\t')
    return result

# connection data for the test database to write the results
connection_test = dict(database='test',
              host='https://clickhouse.lab.karpov.courses',
              user='student-rw',
              password='656e2b0c9c')



# Tasks default parameters
# more info by the link
# https://airflow.apache.org/docs/apache-airflow/1.10.6/_api/airflow/models/index.html#airflow.models.BaseOperator

default_args = {
    'owner': 'v-hudokormov-21',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2022, 2, 11),
}

# Dag time start in cron type

schedule_interval = '0 23 * * *'

# dag tutorial 
# https://airflow.apache.org/docs/apache-airflow/1.10.6/tutorial.html?highlight=email
# context variables usage link
# https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html

@dag(default_args=default_args, schedule_interval=schedule_interval, catchup=False)
def dag_etl_khudokormov():

    @task()
    def extract():
        query = """
SELECT * 
FROM (
    SELECT *
    FROM (
        --the full list of users from message_actions
        SELECT user_id,
            any(age) AS age,
            any(gender) AS gender,
            any(os) AS os
        FROM simulator_20230120.message_actions
        GROUP BY user_id
        ) AS info_from_messages
    FULL OUTER JOIN
        (
        --the full list of users from feed_actions
        SELECT user_id,
        any(age) AS age,
        any(gender) AS gender,
        any(os) AS os
        FROM simulator_20230120.feed_actions
        GROUP BY user_id
        ) AS info_from_feed
    USING user_id, age, gender, os
    ) AS user_dimensions
RIGHT JOIN 
    (-- right join to the table with metrics information
        SELECT *
        FROM 
        (SELECT user_id, 
        views,
        likes,
        messages_sent,
        messages_received
        FROM (
        -- list of user likes&views from feed
        SELECT
            user_id,
            countIf(action = 'view') AS views,
            countIf(action = 'like') AS likes
        FROM simulator_20230120.feed_actions
        WHERE toDate(time) = toDate(today())-1
        GROUP BY user_id
            ) AS user_likes_views
    FULL OUTER JOIN
        (
        -- list of user messages sent/received 
        SELECT user_id,
            q1.messages_sent,
            q2.messages_received
        FROM (
            -- list of user messages sent
            SELECT user_id,
                    COUNT(user_id) AS messages_sent
            FROM simulator_20230120.message_actions
            WHERE toDate(time) = today() - 1
            GROUP BY user_id
            ) AS q1
        FULL OUTER JOIN (
            -- list of user messages received
            SELECT reciever_id AS user_id,
                    COUNT(reciever_id) AS messages_received
            FROM simulator_20230120.message_actions
            WHERE toDate(time) = today() -1
            GROUP BY user_id
            ) AS q2
        USING user_id
        ) AS user_messages
        USING user_id
        ) AS user_likes_views_messages
        FULL OUTER JOIN 
        (
        SELECT user_id,
        users_sent,
        users_received
        FROM (
            -- count users_sent - how much users received the message from the current user
            SELECT user_id, COUNT(DISTINCT reciever_id) AS users_sent
            FROM simulator_20230120.message_actions
            WHERE toDate(time) = today() - 1
            GROUP BY user_id
            ) AS user_messages_sent
        FULL OUTER JOIN 
            (
            -- count users_received - how much users sent the messages to the current user
            SELECT reciever_id AS user_id, users_received
            FROM (
                SELECT reciever_id, COUNT(DISTINCT user_id) AS users_received
                FROM simulator_20230120.message_actions
                WHERE toDate(time) = today() - 1
                GROUP BY reciever_id
                )
            ) AS user_messages_received
        USING user_id
        ) AS user_likes_views_messages_sender
        USING user_id
    ) AS user_messages_views_combined
    USING user_id
format TSVWithNames
        """
        data = ch_get_data(query=query)
        return data

    @task
    def transfrom_age(data):
        context = get_current_context()
        date_previuos_day  = ds_add(context['ds'], -1)
        df_age = data[['age', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]\
                    .groupby('age', as_index=False)\
                    .sum()
        df_age['event_date'] = date_previuos_day
        df_age['dimension'] = 'age'
        df_age = df_age.rename(columns = {'age':'dimension_value'})
        df_age = df_age[['event_date', 'dimension', 'dimension_value', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]
        return df_age

    @task
    def transfrom_gender(data):
        context = get_current_context()
        date_previuos_day  = ds_add(context['ds'], -1)
        df_gender = data[['gender', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]\
            .groupby('gender', as_index=False)\
            .sum()
        df_gender['event_date'] = date_previuos_day
        df_gender['dimension'] = 'gender'
        df_gender = df_gender.rename(columns = {'gender':'dimension_value'})
        df_gender = df_gender[['event_date', 'dimension', 'dimension_value', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]
        return df_gender

    @task
    def transfrom_os(data):
        context = get_current_context()
        date_previuos_day  = ds_add(context['ds'], -1)
        df_os = data[['os', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]\
            .groupby('os', as_index=False)\
            .sum()
        df_os['event_date'] = date_previuos_day
        df_os['dimension'] = 'os'
        df_os = df_os.rename(columns = {'os':'dimension_value'})
        df_os = df_os[['event_date', 'dimension', 'dimension_value', 'views', 'likes', 'messages_received', 'messages_sent', 'users_received', 'users_sent']]
        return df_os


    @task
    def load(df_age, df_gender, df_os):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS test.v_khudokormov_etl_result
            (
            dimension String,
            dimension_value String,
            event_date Date,
            likes UInt64,
            views UInt64,
            messages_received UInt64,
            messages_sent UInt64,
            users_received UInt64,
            users_sent UInt64
            )
            ENGINE = MergeTree()
            ORDER BY event_date
        """
        # creating the table in db
        ph.execute(create_table_query, connection=connection_test)
        # loading data to the database
        ph.to_clickhouse(df = pd.concat([df_age, df_gender, df_os], ignore_index=True),
                        table = 'v_khudokormov_etl_result',
                        index = False,
                        connection=connection_test)

    data = extract()
    df_age = transfrom_age(data)
    df_gender = transfrom_gender(data)
    df_os = transfrom_os(data)
    load(df_age, df_gender, df_os)


dag_etl_khudokormov = dag_etl_khudokormov()
