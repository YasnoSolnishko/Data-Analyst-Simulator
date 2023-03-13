import pandas as pd
import telegram
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import io
import requests

from airflow.decorators import dag, task

sns.set()

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


def get_plot(data_feed, data_msg, data_DAU_all, data_new_users):
    data = pd.merge(data_feed, data_msg, on="date")
    data = pd.merge(data, data_DAU_all, on="date")
    data = pd.merge(data, data_new_users, on="date")
    data["events_all"] = data["events"] + data["msgs"]

    plot_objects = []

    fig, axes = plt.subplots(3, figsize=(10, 14))
    fig.suptitle("Application statistic for 7 days")
    app_dict = {
        0: {"y": ["events"], "title": "Events"},
        1: {"y": ["users", "users_ios", "users_android"], "title": "DAU"},
        2: {
            "y": ["new_users", "new_users_ads", "new_users_organic"],
            "title": "New users",
        },
    }
    for i in range(3):
        for y in app_dict[i]["y"]:
            sns.lineplot(ax=axes[i], data=data, x="date", y=y)

        axes[i].set_title(app_dict[(i)]["title"])
        axes[i].set(xlabel=None)
        axes[i].set(ylabel=None)
        axes[i].legend(app_dict[i]["y"])
        for ind, label in enumerate(axes[i].get_xticklabels()):
            if ind % 3 == 0:
                label.set_visible(True)
            else:
                label.set_visible(False)

    plot_object = io.BytesIO()
    plt.savefig(plot_object)
    plot_object.name = "app_stat.png"
    plot_object.seek(0)
    plt.close()
    plot_objects.append(plot_object)

    fig, axes = plt.subplots(2, 2, figsize=(10, 14))
    fig.suptitle("Feed statistic for 7 days")
    plot_dict = {
        (0, 0): {"y": "feed_users", "title": "Unique users"},
        (0, 1): {"y": "views", "title": "Views"},
        (1, 0): {"y": "likes", "title": "Likes"},
        (1, 1): {"y": "ctr", "title": "CTR"},
    }

    for i in range(2):
        for j in range(2):
            sns.lineplot(
                ax=axes[i, j], data=data, x="date", y=plot_dict[(i, j)]["y"]
            )
            axes[i, j].set_title(plot_dict[(i, j)]["title"])
            axes[i, j].set(xlabel=None)
            axes[i, j].set(ylabel=None)
            for ind, label in enumerate(axes[i, j].get_xticklabels()):
                if ind % 3 == 0:
                    label.set_visible(True)
                else:
                    label.set_visible(False)

    plot_object = io.BytesIO()
    plt.savefig(plot_object)
    plot_object.name = "feed_stat.png"
    plot_object.seek(0)
    plt.close()
    plot_objects.append(plot_object)

    fig, axes = plt.subplots(3, figsize=(10, 14))
    fig.suptitle("Messenger statistic for 7 days")
    msg_dict = {
        0: {"y": "users_msgs", "title": "DAU"},
        1: {"y": "msgs", "title": "Messages"},
        2: {"y": "mpu", "title": "Messages per user"},
    }
    for i in range(3):
        sns.lineplot(ax=axes[i], data=data, x="date", y=msg_dict[i]["y"])

        axes[i].set_title(app_dict[(i)]["title"])
        axes[i].set(xlabel=None)
        axes[i].set(ylabel=None)
        for ind, label in enumerate(axes[i].get_xticklabels()):
            if ind % 3 == 0:
                label.set_visible(True)
            else:
                label.set_visible(False)

    plot_object = io.BytesIO()
    plt.savefig(plot_object)
    plot_object.name = "msngr_stat.png"
    plot_object.seek(0)
    plt.close()
    plot_objects.append(plot_object)

    return plot_objects


@dag(
    default_args=default_args,
    schedule_interval=schedule_interval,
    catchup=False,
)
def dag_app_report_khudokormov():
    @task()
    def app_report(chat=None):
        chat_id = chat or -677113209
        bot_token = ""
        bot = telegram.Bot(bot_token)

        report_text = """Application report for {date}
    Event total: {events}
    👤DAU: {users} ({to_users_day_ago:+.2%} to day ago, {to_users_week_ago:+.2%} to week ago)
    👤DAU by platform:
        🍏iOS: {users_ios} ({to_users_ios_day_ago:+.2%} to day ago, {to_users_ios_week_ago:+.2%} to week ago)
        🥑Android: {users_android} ({to_users_android_day_ago:+.2%} to day ago, {to_users_android_week_ago:+.2%} to week ago)
    👥New users: {new_users} ({to_new_users_day_ago:+.2%} to day ago, {to_new_users_week_ago:+.2%} to week ago)
    👥New users by source:
        🧲ads: {new_users_ads} ({to_new_users_ads_day_ago:+.2%} to day ago, {to_new_users_ads_week_ago:+.2%} to week ago)
        🍀organic: {new_users_organic} ({to_new_users_organic_day_ago:+.2%} to day ago, {to_new_users_organic_week_ago:+.2%} to week ago)

    FEED:
    👤DAU: {feed_users} ({to_feed_users_day_ago:+.2%} to day ago, {to_feed_users_week_ago:+.2%} to week ago)
    ❤️Likes: {likes} ({to_likes_day_ago:+.2%} to day ago, {to_likes_week_ago:+.2%} to week ago)
    👀Views: {views} ({to_views_day_ago:+.2%} to day ago, {to_views_week_ago:+.2%} to week ago) 
    🎯CTR: {ctr:.2f}% ({to_ctr_day_ago:+.2%} to day ago, {to_ctr_week_ago:+.2%} to week ago)
    📝Posts: {posts} ({to_posts_day_ago:+.2%} to day ago, {to_posts_week_ago:+.2%} to week ago)
    ❣️Likes per user: {lpu:.2f} ({to_lpu_day_ago:+.2%} to day ago, {to_lpu_week_ago:+.2%} to week ago)

    MESSENGER:
    👤DAU: {msg_users} ({to_msg_users_day_ago:+.2%} to day ago, {to_msg_users_week_ago:+.2%} to week ago)
    📝Messages: {msgs} ({to_msgs_day_ago:+.2%} to day ago, {to_msgs_week_ago:+.2%} to week ago)
    📨Messages per user: {mpu:.2f} ({to_mpu_day_ago:+.2%} to day ago, {to_mpu_week_ago:+.2%} to week ago) 
    """

        query = """      
                SELECT 
                    toDate(time) AS date
                    , uniqExact(user_id) AS feed_users
                    , countIf(user_id, action = 'view') AS views
                    , countIf(user_id, action = 'like') AS likes
                    , likes / views * 100 AS ctr
                    , views + likes AS events
                    , uniqExact(post_id) AS posts
                    , likes / feed_users AS lpu
                FROM simulator_20230120.feed_actions
                WHERE toDate(time) BETWEEN today()-8 AND today() - 1
                GROUP BY date
                ORDER BY date"""
        data_feed = ch_get_data(query=query)

        query = """      
                SELECT 
                    toDate(time) AS date
                    , uniqExact(user_id) AS users_msgs
                    , COUNT(user_id) AS msgs
                    , msgs / users_msgs AS mpu
                FROM simulator_20230120.message_actions
                WHERE toDate(time) BETWEEN today()-8 AND today() - 1
                GROUP BY date
                ORDER BY date"""
        data_msg = ch_get_data(query=query)

        query = """
                SELECT    date
                        , uniqExact(user_id) as users
                        , uniqExactIf(user_id, os='iOS') as users_ios
                        , uniqExactIf(user_id, os='Android') as users_android
                FROM (
                        SELECT distinct
                            toDate(time) as date
                            , user_id
                            , os
                        FROM simulator_20230120.feed_actions
                        WHERE toDate(time) BETWEEN today()-8 AND today() - 1

                        UNION ALL

                        SELECT distinct
                            toDate(time) as date
                            , user_id
                            , os
                        FROM simulator_20230120.message_actions
                        WHERE toDate(time) BETWEEN today()-8 AND today() - 1
                    ) as q1
                GROUP BY date
                ORDER BY date"""
        data_DAU_all = ch_get_data(query=query)

        query = """
                SELECT
                        date
                        , uniqExact(user_id) as new_users
                        , uniqExactIf(user_id, source = 'ads') as new_users_ads
                        , uniqExactIf(user_id, source = 'organic') as new_users_organic
                FROM (
                        SELECT
                                user_id
                                , source
                                , min(min_dt) as date
                        FROM (
                                SELECT    user_id
                                        , min(toDate(time)) as min_dt
                                        , source
                                FROM simulator_20230120.feed_actions
                                WHERE toDate(time) BETWEEN today() - 90 AND today() - 1
                                GROUP BY user_id, source

                                UNION ALL

                                SELECT    user_id
                                        , min(toDate(time)) as min_dt
                                        , source
                                FROM simulator_20230120.message_actions
                                WHERE toDate(time) BETWEEN today() - 90 AND today() - 1
                                GROUP BY user_id, source
                            ) as q1
                        GROUP BY user_id, source
                    ) q2
                WHERE date BETWEEN today()-8 AND today()-1
                GROUP BY date"""
        data_new_users = ch_get_data(query=query)

        today = pd.Timestamp("now") - pd.DateOffset(days=1)
        day_ago = today - pd.DateOffset(days=1)
        week_ago = today - pd.DateOffset(days=7)

        data_feed["date"] = pd.to_datetime(data_feed["date"]).dt.date
        data_DAU_all["date"] = pd.to_datetime(data_DAU_all["date"]).dt.date
        data_msg["date"] = pd.to_datetime(data_msg["date"]).dt.date
        data_new_users["date"] = pd.to_datetime(data_new_users["date"]).dt.date

        data_feed = data_feed.astype(
            {
                "feed_users": int,
                "views": int,
                "likes": int,
                "events": int,
                "posts": int,
            }
        )

        data_DAU_all = data_DAU_all.astype(
            {"users": int, "users_ios": int, "users_android": int}
        )

        data_msg = data_msg.astype({"users_msgs": int, "msgs": int})

        data_new_users = data_new_users.astype(
            {"new_users": int, "new_users_ads": int, "new_users_organic": int}
        )

        report = report_text.format(
            date=today.date(),
            events=data_feed[data_feed["date"] == today.date()]["views"].iloc[
                0
            ]
            + data_feed[data_feed["date"] == today.date()]["likes"].iloc[0]
            + data_msg[data_msg["date"] == today.date()]["msgs"].iloc[0],
            users=data_DAU_all[data_DAU_all["date"] == today.date()][
                "users"
            ].iloc[0],
            to_users_day_ago=(
                data_DAU_all[data_DAU_all["date"] == today.date()][
                    "users"
                ].iloc[0]
                - data_DAU_all[data_DAU_all["date"] == day_ago.date()][
                    "users"
                ].iloc[0]
            )
            / data_DAU_all[data_DAU_all["date"] == day_ago.date()][
                "users"
            ].iloc[0],
            to_users_week_ago=(
                data_DAU_all[data_DAU_all["date"] == today.date()][
                    "users"
                ].iloc[0]
                - data_DAU_all[data_DAU_all["date"] == week_ago.date()][
                    "users"
                ].iloc[0]
            )
            / data_DAU_all[data_DAU_all["date"] == week_ago.date()][
                "users"
            ].iloc[0],
            users_ios=data_DAU_all[data_DAU_all["date"] == today.date()][
                "users_ios"
            ].iloc[0],
            to_users_ios_day_ago=(
                data_DAU_all[data_DAU_all["date"] == today.date()][
                    "users_ios"
                ].iloc[0]
                - data_DAU_all[data_DAU_all["date"] == day_ago.date()][
                    "users_ios"
                ].iloc[0]
            )
            / data_DAU_all[data_DAU_all["date"] == day_ago.date()][
                "users_ios"
            ].iloc[0],
            to_users_ios_week_ago=(
                data_DAU_all[data_DAU_all["date"] == today.date()][
                    "users_ios"
                ].iloc[0]
                - data_DAU_all[data_DAU_all["date"] == week_ago.date()][
                    "users_ios"
                ].iloc[0]
            )
            / data_DAU_all[data_DAU_all["date"] == week_ago.date()][
                "users_ios"
            ].iloc[0],
            users_android=data_DAU_all[data_DAU_all["date"] == today.date()][
                "users_android"
            ].iloc[0],
            to_users_android_day_ago=(
                data_DAU_all[data_DAU_all["date"] == today.date()][
                    "users_android"
                ].iloc[0]
                - data_DAU_all[data_DAU_all["date"] == day_ago.date()][
                    "users_android"
                ].iloc[0]
            )
            / data_DAU_all[data_DAU_all["date"] == day_ago.date()][
                "users_android"
            ].iloc[0],
            to_users_android_week_ago=(
                data_DAU_all[data_DAU_all["date"] == today.date()][
                    "users_android"
                ].iloc[0]
                - data_DAU_all[data_DAU_all["date"] == week_ago.date()][
                    "users_android"
                ].iloc[0]
            )
            / data_DAU_all[data_DAU_all["date"] == week_ago.date()][
                "users_android"
            ].iloc[0],
            new_users=data_new_users[data_new_users["date"] == today.date()][
                "new_users"
            ].iloc[0],
            to_new_users_day_ago=(
                data_new_users[data_new_users["date"] == today.date()][
                    "new_users"
                ].iloc[0]
                - data_new_users[data_new_users["date"] == day_ago.date()][
                    "new_users"
                ].iloc[0]
            )
            / data_new_users[data_new_users["date"] == day_ago.date()][
                "new_users"
            ].iloc[0],
            to_new_users_week_ago=(
                data_new_users[data_new_users["date"] == today.date()][
                    "new_users"
                ].iloc[0]
                - data_new_users[data_new_users["date"] == week_ago.date()][
                    "new_users"
                ].iloc[0]
            )
            / data_new_users[data_new_users["date"] == week_ago.date()][
                "new_users"
            ].iloc[0],
            new_users_ads=data_new_users[
                data_new_users["date"] == today.date()
            ]["new_users_ads"].iloc[0],
            to_new_users_ads_day_ago=(
                data_new_users[data_new_users["date"] == today.date()][
                    "new_users_ads"
                ].iloc[0]
                - data_new_users[data_new_users["date"] == day_ago.date()][
                    "new_users_ads"
                ].iloc[0]
            )
            / data_new_users[data_new_users["date"] == day_ago.date()][
                "new_users_ads"
            ].iloc[0],
            to_new_users_ads_week_ago=(
                data_new_users[data_new_users["date"] == today.date()][
                    "new_users_ads"
                ].iloc[0]
                - data_new_users[data_new_users["date"] == week_ago.date()][
                    "new_users_ads"
                ].iloc[0]
            )
            / data_new_users[data_new_users["date"] == week_ago.date()][
                "new_users_ads"
            ].iloc[0],
            new_users_organic=data_new_users[
                data_new_users["date"] == today.date()
            ]["new_users_organic"].iloc[0],
            to_new_users_organic_day_ago=(
                data_new_users[data_new_users["date"] == today.date()][
                    "new_users_organic"
                ].iloc[0]
                - data_new_users[data_new_users["date"] == day_ago.date()][
                    "new_users_organic"
                ].iloc[0]
            )
            / data_new_users[data_new_users["date"] == day_ago.date()][
                "new_users_organic"
            ].iloc[0],
            to_new_users_organic_week_ago=(
                data_new_users[data_new_users["date"] == today.date()][
                    "new_users_organic"
                ].iloc[0]
                - data_new_users[data_new_users["date"] == week_ago.date()][
                    "new_users_organic"
                ].iloc[0]
            )
            / data_new_users[data_new_users["date"] == week_ago.date()][
                "new_users_organic"
            ].iloc[0],
            feed_users=data_feed[data_feed["date"] == today.date()][
                "feed_users"
            ].iloc[0],
            to_feed_users_day_ago=(
                data_feed[data_feed["date"] == today.date()][
                    "feed_users"
                ].iloc[0]
                - data_feed[data_feed["date"] == day_ago.date()][
                    "feed_users"
                ].iloc[0]
            )
            / data_feed[data_feed["date"] == day_ago.date()][
                "feed_users"
            ].iloc[0],
            to_feed_users_week_ago=(
                data_feed[data_feed["date"] == today.date()][
                    "feed_users"
                ].iloc[0]
                - data_feed[data_feed["date"] == week_ago.date()][
                    "feed_users"
                ].iloc[0]
            )
            / data_feed[data_feed["date"] == week_ago.date()][
                "feed_users"
            ].iloc[0],
            likes=data_feed[data_feed["date"] == today.date()]["likes"].iloc[
                0
            ],
            to_likes_day_ago=(
                data_feed[data_feed["date"] == today.date()]["likes"].iloc[0]
                - data_feed[data_feed["date"] == day_ago.date()]["likes"].iloc[
                    0
                ]
            )
            / data_feed[data_feed["date"] == day_ago.date()]["likes"].iloc[0],
            to_likes_week_ago=(
                data_feed[data_feed["date"] == today.date()]["likes"].iloc[0]
                - data_feed[data_feed["date"] == week_ago.date()][
                    "likes"
                ].iloc[0]
            )
            / data_feed[data_feed["date"] == week_ago.date()]["likes"].iloc[0],
            views=data_feed[data_feed["date"] == today.date()]["views"].iloc[
                0
            ],
            to_views_day_ago=(
                data_feed[data_feed["date"] == today.date()]["views"].iloc[0]
                - data_feed[data_feed["date"] == day_ago.date()]["views"].iloc[
                    0
                ]
            )
            / data_feed[data_feed["date"] == day_ago.date()]["views"].iloc[0],
            to_views_week_ago=(
                data_feed[data_feed["date"] == today.date()]["views"].iloc[0]
                - data_feed[data_feed["date"] == week_ago.date()][
                    "views"
                ].iloc[0]
            )
            / data_feed[data_feed["date"] == week_ago.date()]["views"].iloc[0],
            ctr=data_feed[data_feed["date"] == today.date()]["ctr"].iloc[0],
            to_ctr_day_ago=(
                data_feed[data_feed["date"] == today.date()]["ctr"].iloc[0]
                - data_feed[data_feed["date"] == day_ago.date()]["ctr"].iloc[0]
            )
            / data_feed[data_feed["date"] == day_ago.date()]["ctr"].iloc[0],
            to_ctr_week_ago=(
                data_feed[data_feed["date"] == today.date()]["ctr"].iloc[0]
                - data_feed[data_feed["date"] == week_ago.date()]["ctr"].iloc[
                    0
                ]
            )
            / data_feed[data_feed["date"] == week_ago.date()]["ctr"].iloc[0],
            posts=data_feed[data_feed["date"] == today.date()]["posts"].iloc[
                0
            ],
            to_posts_day_ago=(
                data_feed[data_feed["date"] == today.date()]["posts"].iloc[0]
                - data_feed[data_feed["date"] == day_ago.date()]["posts"].iloc[
                    0
                ]
            )
            / data_feed[data_feed["date"] == day_ago.date()]["posts"].iloc[0],
            to_posts_week_ago=(
                data_feed[data_feed["date"] == today.date()]["posts"].iloc[0]
                - data_feed[data_feed["date"] == week_ago.date()][
                    "posts"
                ].iloc[0]
            )
            / data_feed[data_feed["date"] == week_ago.date()]["posts"].iloc[0],
            lpu=data_feed[data_feed["date"] == today.date()]["lpu"].iloc[0],
            to_lpu_day_ago=(
                data_feed[data_feed["date"] == today.date()]["lpu"].iloc[0]
                - data_feed[data_feed["date"] == day_ago.date()]["lpu"].iloc[0]
            )
            / data_feed[data_feed["date"] == day_ago.date()]["lpu"].iloc[0],
            to_lpu_week_ago=(
                data_feed[data_feed["date"] == today.date()]["lpu"].iloc[0]
                - data_feed[data_feed["date"] == week_ago.date()]["lpu"].iloc[
                    0
                ]
            )
            / data_feed[data_feed["date"] == week_ago.date()]["lpu"].iloc[0],
            msg_users=data_msg[data_msg["date"] == today.date()][
                "users_msgs"
            ].iloc[0],
            to_msg_users_day_ago=(
                data_msg[data_msg["date"] == today.date()]["users_msgs"].iloc[
                    0
                ]
                - data_msg[data_msg["date"] == day_ago.date()][
                    "users_msgs"
                ].iloc[0]
            )
            / data_msg[data_msg["date"] == day_ago.date()]["users_msgs"].iloc[
                0
            ],
            to_msg_users_week_ago=(
                data_msg[data_msg["date"] == today.date()]["users_msgs"].iloc[
                    0
                ]
                - data_msg[data_msg["date"] == week_ago.date()][
                    "users_msgs"
                ].iloc[0]
            )
            / data_msg[data_msg["date"] == week_ago.date()]["users_msgs"].iloc[
                0
            ],
            msgs=data_msg[data_msg["date"] == today.date()]["msgs"].iloc[0],
            to_msgs_day_ago=(
                data_msg[data_msg["date"] == today.date()]["msgs"].iloc[0]
                - data_msg[data_msg["date"] == day_ago.date()]["msgs"].iloc[0]
            )
            / data_msg[data_msg["date"] == day_ago.date()]["msgs"].iloc[0],
            to_msgs_week_ago=(
                data_msg[data_msg["date"] == today.date()]["msgs"].iloc[0]
                - data_msg[data_msg["date"] == week_ago.date()]["msgs"].iloc[0]
            )
            / data_msg[data_msg["date"] == week_ago.date()]["msgs"].iloc[0],
            mpu=data_msg[data_msg["date"] == today.date()]["mpu"].iloc[0],
            to_mpu_day_ago=(
                data_msg[data_msg["date"] == today.date()]["mpu"].iloc[0]
                - data_msg[data_msg["date"] == day_ago.date()]["mpu"].iloc[0]
            )
            / data_msg[data_msg["date"] == day_ago.date()]["mpu"].iloc[0],
            to_mpu_week_ago=(
                data_msg[data_msg["date"] == today.date()]["mpu"].iloc[0]
                - data_msg[data_msg["date"] == week_ago.date()]["mpu"].iloc[0]
            )
            / data_msg[data_msg["date"] == week_ago.date()]["mpu"].iloc[0],
        )

        plot_objects = get_plot(
            data_feed, data_msg, data_DAU_all, data_new_users
        )
        send_message(bot_token, chat_id, report)
        for plot_object in plot_objects:
            send_plot(bot_token, chat_id, plot_object)


dag_app_report_khudokormov = dag_app_report_khudokormov()
