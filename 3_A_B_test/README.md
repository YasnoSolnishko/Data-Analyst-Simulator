## A/A test
### Description
There is an AA test data from '2022-12-25' to '2022-12-31'. The task is to simulate as if we conducted 10,000 AA tests. At each iteration, you need to form non-repeating sub-samples of 500 users from the 2 and 3 experimental groups. Conduct a comparison of these sub-samples using a t-test.
### Task
1. Build a histogram of the distribution of the resulting 10,000 p-values.
2. Calculate the percentage of p-values that are less than or equal to 0.05.
3. Write a conclusion about the conducted AA test, whether our splitting system works correctly.
### Result
The tests is done ([link](https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/3_A_B_test/AA_test.ipynb))  
<img src="https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/3_A_B_test/AA_test_diagram.png" width="400"/>   
The distribution of the p-value is uniform.  
In an A/A t-test that satisfies the underlying statistical assumptions for a t-test, the resulting p-value distribution should be uniform (so, a p-value < 0.05 should occur 5% of the time). If the p-value distribution is not uniform, it shows that the testing methodology is flawed and violates assumptions.
The calculation shows that a p-value < 0.05 occurs less than 5% of the time, which means that the split system works correctly.

## A/B test
The experiment took place from 2023-01-01 to 2023-01-07 inclusive, with two groups involved: Group 2 used one of the new post recommendation algorithms, while Group 1 was used as control.
The main hypothesis is that the new algorithm in Group 2 will lead to an increase in CTR.
### Task
The task is to analyze the AB test data.

1. Choose a method of analysis and compare the CTR in the two groups (we discussed t-test, Poisson bootstrap, Mann-Whitney test, smoothed CTR t-test (α=5), and t-test and Mann-Whitney test on bucketed data).
2. Compare the data using these tests. Also, visually inspect the distributions. Why did the tests perform the way they did?
3. Describe a potential situation in which such a change could have occurred. There is no perfect answer, so think about it.
4. Write a recommendation on whether to roll out the new algorithm to all new users or not.
### Result
The tests is done ([link](https://github.com/YasnoSolnishko/Data-Analyst-Simulator/blob/main/3_A_B_test/AB_test.ipynb))
#### Tests table
Below is the summary table of test results:
| Test                           | Comparison objects | Different? |
|--------------------------------|--------------------|------------|
| t-test                         | CTR means          | False      |
| Mann–Whitney U test            | distribution       | True       |
| Poisson bootstrap              | CTR means          | True       |
| T-test with smoothed CTR (α=5) | CTR means          | False      |
| T-test over bucket             | CTR means          | True       |
| Mann–Whitney over bucket       | distribution       | True       |

First of all, from Diagrams [3.1](#diagram_3_1) and [3.2](#diagram_3_2), we can see that there is a difference between of CTR distribution in the groups. Group 1 has a normal unimodal distribution, but group 2 has a bimodal distribution.  
The reasons for bimodal distribution could be next:
* not correct splitting (AA test is done in [Appendix A](appendix_a)). The results show that the split is correct. But I repeated the AA test several times, and in some cases, it showed an error above 5% which could mean that the split is not 100% correct or there needs more data.
* two different samples are mixed into group 2 (not confirmed by AA test in [Appendix A](appendix_a))
* the new algorithm created two groups (A & B) inside the test group. For group A, the CTR decreased; for group B, CTR increased, but the mean CTR was the same (that is confirmed by T-test).
#### Conclusions
The results look messy; some t-tests show the difference in mean CTRs, and others do not.  
Mann-Whitney test shows that the distribution is different, but that is obvious if one looks at the diagrams of CTR distributions. It seems like that for some users new algorithm increased CTR, and for others decreased it. 
Poisson bootstrap shows a difference between the average CTRs. Since the bootstrap is the simulation of the "general population", it could mean that there is a real difference between average CTRs, but we do not have enough data to access it correctly.
#### Recommendations
In such an unclear situation, I would not recommend implementing the algorithm which was used for group 2 in AB-test. 

However, the data could be used to investigate the groups inside group 2 to identify if there is any correlation between the people for which CTR increased/decreased. For example, for people younger than 30, the new algorithm increases CTR, but for those older than 30, vice versa.
And if this hypothesis is confirmed, the new algorithm could be implemented for the corresponding group.
