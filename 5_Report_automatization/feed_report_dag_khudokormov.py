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

# Get data from clickhouse

bot = telegram.Bot(token=KC_analyst_simulator_bot_token)
chat_id = -677113209


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


def send_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}"
    payload = {"text": message}
    requests.post(url, json=payload)


def send_plot(bot_token, chat_id, plot):
    url = (
        f"https://api.telegram.org/bot{bot_token}/sendPhoto?chat_id={chat_id}"
    )
    files = {"photo": plot}
    requests.post(url, files=files)


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

schedule_interval = "00 11 * * *"

# dag tutorial
# https://airflow.apache.org/docs/apache-airflow/1.10.6/tutorial.html?highlight=email
# context variables usage link
# https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html


@dag(
    default_args=default_args,
    schedule_interval=schedule_interval,
    catchup=False,
)
def dag_report_khudokormov():
    @task()
    def extract():
        query = """
SELECT toDate(time) as date,
        COUNT (DISTINCT user_id) AS users,
        countIf (action, action = 'view') AS views,
        countIf (action, action = 'like') AS likes,
        countIf (action, action = 'like') / countIf (action, action = 'view') AS ctr
FROM simulator_20230120.feed_actions
WHERE toDate(time) BETWEEN toDate(today()) - 7 AND toDate(today()-1)
GROUP BY date
format TSVWithNames
        """

        data = ch_get_data(query=query)
        return data

    @task()
    def get_report(data):
        today = date.today()
        yesterday = today - timedelta(days=1)
        # dby - day before yesterday
        dby = yesterday - timedelta(days=1)

        # calculating metrics
        yesterday_DAU = data[data.date == str(yesterday)].users.to_list()[0]
        yesterday_views = data[data.date == str(yesterday)].views.to_list()[0]
        yesterday_likes = data[data.date == str(yesterday)].likes.to_list()[0]
        yesterday_ctr = (
            data[data.date == str(yesterday)].ctr.to_list()[0] * 100
        )

        # calculating changes comparing with the day before yesterday
        DAU_change = (
            (yesterday_DAU - data[data.date == str(dby)].users.to_list()[0])
            / data[data.date == str(dby)].users.to_list()[0]
            * 100
        )
        views_change = (
            (yesterday_views - data[data.date == str(dby)].views.to_list()[0])
            / data[data.date == str(dby)].views.to_list()[0]
            * 100
        )
        likes_change = (
            (yesterday_likes - data[data.date == str(dby)].likes.to_list()[0])
            / data[data.date == str(dby)].likes.to_list()[0]
            * 100
        )
        ctr_change = (
            (
                yesterday_ctr / 100
                - data[data.date == str(dby)].ctr.to_list()[0]
            )
            / data[data.date == str(dby)].ctr.to_list()[0]
            * 100
        )

        # creating the report text
        report_text = f"""Hello, Username.
        The report for the date {yesterday} is below.
        Change is comparing with the previuos day
        DAU\t= {yesterday_DAU} change {round(DAU_change, 2)} %
        Views\t= {yesterday_views} change {round(views_change, 2)} %
        Likes\t= {yesterday_likes} change {round(likes_change, 2)} %
        CTR\t= {round(yesterday_ctr, 2)} %  change {round(ctr_change, 2)} %
        """
        # plot_1 = create_plot(data, "date", "users", "DAU")
        # plot_2 = create_plot(data, "date", "views", "Views")
        # plot_3 = create_plot(data, "date", "likes", "Likes")
        # plot_4 = create_plot(data, "date", "ctr", "CTR")
        return report_text

    @task()
    def get_DAU_plot(data):
        plot = create_plot(data, "date", "users", "DAU")
        return plot

    @task()
    def get_Views_plot(data):
        plot = create_plot(data, "date", "views", "Views")
        return plot

    @task()
    def get_Likes_plot(data):
        plot = create_plot(data, "date", "likes", "Likes")
        return plot

    @task()
    def get_CTR_plot(data):
        plot = create_plot(data, "date", "ctr", "CTR")
        return plot

    @task()
    def load(bot_token, chat_id, report_text, plot_1, plot_2, plot_3, plot_4):
        # sending the report
        send_message(bot_token, chat_id, report_text)
        # sending diagrams
        send_plot(bot_token, chat_id, plot_1)
        send_plot(bot_token, chat_id, plot_2)
        send_plot(bot_token, chat_id, plot_3)
        send_plot(bot_token, chat_id, plot_4)

    data = extract()
    report = get_report(data)
    plot_1 = get_DAU_plot(data)
    plot_2 = get_Views_plot(data)
    plot_3 = get_Likes_plot(data)
    plot_4 = get_CTR_plot(data)
    load(
        KC_analyst_simulator_bot_token,
        chat_id,
        report,
        plot_1,
        plot_2,
        plot_3,
        plot_4,
    )


dag_report_khudokormov = dag_report_khudokormov()
