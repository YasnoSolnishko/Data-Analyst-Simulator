# Alarm system
## Task
Create alarm system for the application. The system should periodically check key metrics every 15 minutes, such as active users in the newsfeed/messenger, views, likes, CTR, and the number of messages sent.

Study the behavior of the metrics and choose the most appropriate method for anomaly detection. In practice, statistical methods are usually applied. 
In the current version, the deviation of the metric value in the current 15-minute interval compared to from the value in the same 15-minute interval a day ago.

In case of detecting an anomalous value, an alert message should be sent to the chat with the following information: the metric, its value, and the deviation magnitude. Additional information can be added to the message to help investigate the causes of the anomaly, such as a graph or links to a dashboard/chart in the BI system.

Example alert template:

```Metric {metric_name} in group {group}.  
Current value {current_x}. Deviation more than {x}%.  
[optional: link to real-time chart of this metric in BI for more flexible viewing]  
[optional: link to real-time dashboard in BI for investigating the situation as a whole]  
@[optional: tag the responsible/most interested person in case of deviation of this specific metric in this group (if such a person exists)]  

[graph]
```
## Instructions

1. Clone the repository
2. In the local copy, create your own folder inside the dags folder - it should have the same name as your username with @ in your GitLab profile
3. Create a DAG there - it should be in a .py format file
4. Push the result (don't forget to pull all the fresh changes to avoid deleting your colleagues' folders!)
5. Enable the DAG when it appears in Airflow

## Results
Python script for Airflow, that works as an Alarm System.([link](https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/6_Alarm_system/alerts_dag_khudokormov.py))

Alarm screenshots from telegram bot:  
<img src="https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/6_Alarm_system/images/alarms_1.png" width="600">  
<img src="https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/6_Alarm_system/images/alarms_2.png" width="600">
