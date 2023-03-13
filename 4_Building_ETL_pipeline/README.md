# Building ETL pipeline
### Task
The task is to build complete ETL pipeline with all the phases: Extract, Transform, Load. The expected output is an Airflow DAG that will run every day to transform previous day data.
1. Process two tables. 
  * In feed_actions, we will calculate the number of views and likes for each user's content. 
  * In message_actions, we will calculate how many messages each user receives and sends, how many people they write to, and how many people write to them. Each output should be in a separate task.
2. Next, merge the two tables into one.
3. For merged table,  calculate all of these metrics broken down by gender, age, and OS. Make three different DAG tasks for each breakdown.
4. Write the final data with all the metrics to a separate table in ClickHouse.
5. Make sure that every day the table updated with new data.

### Notes
The structure of the final table should be:

Date - event_date  
Slice name - dimension  
Slice value - dimension_value  
Number of views - views  
Number of likes - likes  
Number of received messages - messages_received  
Number of sent messages - messages_sent  
Number of users who received messages - users_received  
Number of users who sent messages - users_sent  
The breakdown is by OS, gender, and age.  

The table should be loaded into the test schema.

## Result
The tasks finished (script by the [link](https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/4_Building_ETL_pipeline/etl_pipeline.py))
The screenshots of DAG in Airflow and result table are below.
![](https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/4_Building_ETL_pipeline/dag_etl_pipeline.png)
![](https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/4_Building_ETL_pipeline/etl_result.png)
