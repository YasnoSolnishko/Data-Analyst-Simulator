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
