# Feed Report
## Task
It's time to automate the basic reporting for our application. Let's set up the automatic sending of an analytical summary to Telegram every morning! What do we need for this:

1. Create your Telegram bot using @BotFather
2. To get the chat_id, use the link https://api.telegram.org/bot<your_bot_token>/getUpdates or the bot.getUpdates() method
3. Write a script for building a news feed report. The report should consist of two parts:
* Text with information on the values of key metrics for the previous day
* A graph with metric values for the previous 7 days. Display the following key metrics in the report:
	* DAU
	* Views
	* Likes
	* CTR
4. Automate the report sending process using Airflow. Put the report building code on GitLab, for this:

## Instructions
1. Clone the repository
2. Inside the dags folder of the local copy, create your own folder that should match your username with @ in your GitLab profile
3. Create a DAG in the folder - it should be in a file with the .py format
4. Push the result
5. Turn on the DAG when it appears in Airflow
6. The report should arrive daily at 11:00 am in the chat.

## Results
Python script is created for Airflow ([link](https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/5_Report_automatization/feed_report_dag_khudokormov.py))
Dag image  
<img src="https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/5_Report_automatization/feed_report_dag.png" width="600">

Report example screenshots  
<img src="https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/5_Report_automatization/report_pics/feed_report_1.png" width="600">  
<img src="https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/5_Report_automatization/report_pics/feed_report_2.png" width="600">
<img src="https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/5_Report_automatization/report_pics/feed_report_3.png" width="600">
<img src="https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/5_Report_automatization/report_pics/feed_report_4.png" width="600">

# Application Report
## Task
Collect a unified report on the performance of the entire application. The report should include information on both the news feed and the messaging service.
Consider what metrics need to be displayed in this report. How can their dynamics be shown? Attach graphs or files to the report to make it more visual and informative. The report should not be just a collection of graphs or text, but help answer business questions about the overall performance of the application.
Automate the report sending using Airflow. Place the code for building the report in GitLab:

## Instructions
1. Clone the repository
2. Inside the dags folder of your local copy, create your own folder - it should have the same name as your username, which is indicated with @ in your GitLab profile
3. Create a DAG there - it should be in a .py file format
4. Push the result
5. Enable the DAG when it appears in Airflow
6. The report should come every day at 11:00 in the chat.

## Results

Python script is created for Airflow ([link](https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/5_Report_automatization/app_report_dag.py))

Report example screenshots  
<img src="https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/5_Report_automatization/report_pics/app_report_1.png" width="600">    
<img src="https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/5_Report_automatization/report_pics/app_report_2.png" width="600">  
<img src="https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/5_Report_automatization/report_pics/app_report_3.png" width="600">
<img src="https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/5_Report_automatization/report_pics/app_report_4.png" width="600">
