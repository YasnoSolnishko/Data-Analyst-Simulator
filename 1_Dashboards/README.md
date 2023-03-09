# Task 1 - Create Dashboards

The main task was to create dashboards covering key audience metrics and events for a news feed product. The task involved adding relevant graphs, slices, and metrics to the dashboards. The goal was to answer the question "how much?" in the initial stages of analytics. The solution required creating an operational dashboard with diagrams for the current day and a primary dashboard for past data. 
The final deliverable are the dashboards. The work mostly was done using Apache Superset, but sometimes I used Redash to write different queries.

## Dashboard 1 - News feed history data
The dashboard provides a comprehensive view of the feed history data through interactive diagrams and KPIs. The main KPIs on the dashboard include DAU, WAU, MAU, users actions with the distinction by action type and platform, and CTR. The dashboard also provides users with four critical KPIs from the previous month, including new posts, total views, total likes, and average CTR.

One of the key features of the dashboard is the ability to filter data based on gender, country, and operating system, which provides valuable insights into user behavior and trends across different segments of the user base. Additionally, the dashboard provides two tables that highlight the top 10 posts and top 10 most active users for the last month, providing a deeper understanding of which posts and users are driving engagement on the platform.
![](https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/1_Dashboards/news-feed-history-data-2023-03-06T12-22.jpg)

## Dashboard 2 - News feed operational data
The dashboard provides a comprehensive view of the feed operational data for the current day, allowing stakeholders to monitor key metrics and make data-driven decisions in real-time.

The dashboard features a KPI that highlights the number of new posts made today, with a sparkline diagram that shows the trend over time and a comparison to the previous day's data. Additionally, there are two diagrams showing the total number of actions and the number of unique users, both with comparisons to the corresponding values from one day and one week ago. These diagrams help to identify trends and patterns in user behavior and engagement over time.

The dashboard also includes three tables that provide insights into the top users of the day, their age, and their country. 

Finally, the dashboard features filtering cells that allow users to filter the data by gender, country, operating system, and post ID, providing deeper insights into user behavior and engagement across different segments of the user base.
![](https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/1_Dashboards/news-feed-operational-data-2023-03-06T12-22.jpg)

## Dashboard 3 - Feed and messenger data
The dashboard features three KPIs, each with a sparkline diagram that shows the trend over time and the percentage change compared to the previous day's data. The first KPI tracks the number of unique feed users, while the second KPI tracks the number of unique messenger users. The third KPI tracks the number of unique users who use both the messenger and feed features, providing valuable insights into how users engage with the platform.

Additionally, the dashboard features two diagrams that show the number of unique daily active users (DAUs) who use both the feed and messenger features and the number of unique users who use the feed feature exclusively. 
![](https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/1_Dashboards/feed-and-messages-2023-03-06T12-23.jpg)
