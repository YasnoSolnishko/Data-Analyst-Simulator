# coding=utf-8

# import required libraries
import telegram
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import io
from datetime import date, datetime, timedelta
import requests
import pandas as pd

from airflow.decorators import dag, task

# bot parameters


bot = telegram.Bot(token=KC_analytics_simulator_bot_token)
chat_id = -677113209

# Get data from clickhouse


def ch_get_data(
    query="Select 1",
    host="https://clickhouse.lab.karpov.courses",
    user="student",
    password="dpo_python_2020",
):
    r = requests.post(
        host, data=query.encode("utf-8"), auth=(user, password), verify=False
    )
    result = pd.read_csv(StringIO(r.text), sep="\t")
    return result


# create a file in buffer for sending
def create_plot(df, x_data, y_data, name):
    sns.lineplot(x=x_data, y=y_data, data=df)
    plt.title(f"{name} - 7 days")
    plt.xticks(rotation=45)
    plot_object = io.BytesIO()
    plt.savefig(plot_object)
    plot_object.seek(0)
    plot_object.name = f"{name}_plot.png"
    plt.close()
    return plot_object


# send message telegram
def send_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}"
    payload = {"text": message}
    requests.post(url, json=payload)


# send image telegram
def send_plot(bot_token, chat_id, plot):
    url = (
        f"https://api.telegram.org/bot{bot_token}/sendPhoto?chat_id={chat_id}"
    )
    files = {"photo": plot}
    requests.post(url, files=files)


def check_anomaly(df, metric, threshold=0.3):
    # the check_anomaly function proposes an algorithm for checking a value for anomaly by means of
    # comparing the value of interest with the value at the same time a day ago
    # if desired, the algorithm inside this function can be changed

    # get the maximum 15-minute from the dataframe - the one that we will check for anomaly
    current_quarter = df["hour_quarter"].max()
    # get the same 15-minute 24 hours ago
    day_ago_quarter = current_quarter - pd.DateOffset(days=1)

    # get the maximum 15-minute from the dataframe
    current_value = df[df["hour_quarter"] == current_quarter][metric].iloc[0]
    # get the same 15-minute 24 hours ago
    day_ago_value = df[df["hour_quarter"] == day_ago_quarter][metric].iloc[0]

    # calculating the deviation
    if current_value <= day_ago_value:
        diff = -1 * abs(current_value / day_ago_value - 1)
    else:
        diff = abs(day_ago_value / current_value - 1)

    # check if the deviation of the metric is greater than the given threshold
    # if the deviation is greater, then return 1, otherwise 0
    if abs(diff) > threshold:
        is_alert = 1
    else:
        is_alert = 0

    return is_alert, current_value, diff


# Tasks default parameters
# more info by the link
# https://airflow.apache.org/docs/apache-airflow/1.10.6/_api/airflow/models/index.html#airflow.models.BaseOperator

default_args = {
    "owner": "v-hudokormov-21",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2022, 2, 11),
}

# Dag time start in cron type

schedule_interval = "01,16,31,46 * * * *"

# dag tutorial
# https://airflow.apache.org/docs/apache-airflow/1.10.6/tutorial.html?highlight=email
# context variables usage link
# https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html


@dag(
    default_args=default_args,
    schedule_interval=schedule_interval,
    catchup=False,
)
def dag_alerts_khudokormov():
    @task()
    def extract_feed_data():
        # get the data for the last 24 hours grouped by 15 minutes interval
        # active users in feed, views, likes, CTR
        query_feed = """
SELECT toStartOfFifteenMinutes(time) as hour_quarter,
        toDate(hour_quarter) as date,
        formatDateTime(hour_quarter, '%R') as hour_min,
        count(DISTINCT user_id) AS 15_min_au,
        countIf(action, action='view') as views,
        countIf(action, action='like') as likes,
        countIf(action, action='like') / countIf(action, action='view') AS ctr
FROM simulator_20230120.feed_actions
GROUP BY hour_quarter
HAVING time > subtractHours(now(), 25)
ORDER BY hour_quarter DESC
format TSVWithNames
        """

        # clickhouse is grouping the data to the start of 15 minutes
        # that means that the datapoint with the time 23:15 will have
        # the data for every second from 23:15:00 to 23:29:29
        # to avoid this I will take only the data for the finished 15 minutes
        # that will have the full data
        # To do that the readings from db to be done in 1, 16, 31 and 46 minutes
        # and the first point (the last in time) to be dropped

        feed_data = ch_get_data(query=query_feed)
        feed_data.drop(index=0, inplace=True)
        feed_data.reset_index(inplace=True, drop=True)
        feed_data["hour_quarter"] = pd.to_datetime(
            feed_data["hour_quarter"], format="%Y-%m-%d %H:%M:%S"
        )

        return feed_data

    @task()
    def extract_messenger_data():
        # get the data for the last 24 hours grouped by 15 minutes interval
        # messenger distinct active users, messages sent
        query_messenger = """
SELECT toStartOfFifteenMinutes(time) as hour_quarter,
        toDate(hour_quarter) as date,
        formatDateTime(hour_quarter, '%R') as hour_min,
        COUNT (DISTINCT user_id) AS 15_min_au,
        COUNT (user_id) AS messages_sent
FROM simulator_20230120.message_actions
GROUP BY hour_quarter
HAVING time > subtractHours(now(), 25)
ORDER BY hour_quarter DESC
format TSVWithNames
        """

        messenger_data = ch_get_data(query=query_messenger)
        messenger_data.drop(index=0, inplace=True)
        messenger_data.reset_index(inplace=True, drop=True)
        messenger_data["hour_quarter"] = pd.to_datetime(
            messenger_data["hour_quarter"], format="%Y-%m-%d %H:%M:%S"
        )

        return messenger_data

    @task
    def run_checking_alerts(df_feed, df_message, chat=None):
        chat_id = chat or -677113209
        bot = telegram.Bot(
            token="6063984268:AAG3uWnhoDUoF-GaQ4FRgBszXIIXyS0ixVE"
        )

        metrics = df_feed.columns[3:]
        for metric in metrics:
            # checking the metric with the check_anomaly function
            is_alert, current_value, diff = check_anomaly(
                df_feed, metric, threshold=0.2
            )
            if is_alert:
                msg = f"""\u2757 \u2757 \u2757 ALARM
                Feed metric {metric}: 
                Current value = {current_value:.0f}
                Deviation from yesterday {diff:.2%}
                """
                # send the alarm
                send_message(KC_analytics_simulator_bot_token, chat_id, msg)

        metrics = df_message.columns[3:]

        for metric in metrics:
            # checking the metric with the check_anomaly function
            is_alert, current_value, diff = check_anomaly(
                df_message, metric, threshold=0.2
            )
            if is_alert:
                msg = f"""\u2757\u2757 \u2757 ALARM
                Messenger metric {metric}: 
                Current value = {current_value:.0f}
                Deviation from yesterday {diff:.2%}
                """
                # send the alarm
                send_message(KC_analytics_simulator_bot_token, chat_id, msg)

    feed_data = extract_feed_data()
    messenger_data = extract_messenger_data()
    run_checking_alerts(feed_data, messenger_data)


dag_alerts_khudokormov = dag_alerts_khudokormov()
