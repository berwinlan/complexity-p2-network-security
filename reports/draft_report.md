# Malware Spread in Mobile Networks - Draft Report


## By: Berwin, Trinity, Miles


### Abstract

The paper we decided to choose investigates how malware spreads in mobile tactical networks using an agent-based model. The paper simulates agents within a military network of Platoons that are composed of Squads that move around and interact with other groups. The probability of interaction between different squads are guided by three different movement patterns: random walk, random waypoint, and hierarchical. Based on each agent’s movements, it impacts their probability of getting infected by malware. The paper compares the rate of malware spread between these three movement patterns of agents and does a parameter sweep for different malware defense percentages and how fast malware spreads between these 3 different movement patterns with different levels of defense against malware. In their results, they identify that malware took the longest to spread in the random walk movement pattern, while malware spread the quickest in the random waypoint movement pattern. Furthermore, they conducted a parameter sweep on how different levels of fortification against malware impacts the spread of malware, which showed that unless defenses were around 80% there was only a slight slowing of malware spread. Overall, the paper identifies different movement configurations and fortification levels to understand at what percentage and what movement resistance to malware is acceptable. In our replication, we were able to replicate the spread rates of 2 out of 3 of the movement patterns.


### Introduction

We used [An agent-based modeling framework for cybersecurity in mobile tactical networks](https://journals.sagepub.com/doi/10.1177/1548512917738858) by Brian Thompson and James Morris-King as a basis for replication.

This paper investigates how malware infiltrates mobile tactical networks given different movement patterns and types of security fortifications against mobile networks through agent based modeling. The paper highlights how even if different mobile networks may be isolated from others, lack of effective security policies coupled with different types of movement interactions can heavily impact malware spread behavior in the overall system. 


### Methodology

The three types of movement the paper investigates are the following:
* Random walk: Squads randomly spawn and random walk independently.
* Random waypoint: Squads randomly spawn, choose a random point, and walk toward that random point until the squad has arrived. Squads are also independent here.
* Hierarchical: Squads begin at their Company’s outpost, which is a randomly selected but constant point. They stay there for a little bit, then go to a random waypoint as a Company. Then, the Squads random walk independently, then the cycle repeats.

TODO: Talk a bit more about the model itself, and how we're getting from walk types to metrics. How does spread actually happen? Maybe figures of what paths look like.

We replicated the experiment that compares the rate of malware spread across three different movement patterns.

![](img/malware_spread.jpeg)



### Replication Results

In our replication, we tested out the random walk and random waypoint movements. We successfully replicated the general shapes of each curve, and we see that like the original experiment, the malware spreads extremely quickly with the random waypoint and much slower with the random walk. Our results of the replication are below:

TODO: Map ticks to hours, run the other one with 80 squads

![](img/replication.png)

Based on our results, we found that the random waypoint movement causes malware to spread more rapidly than the random walk movement. Although agents’ maximum step size is the same in all of the movement patterns, the agents end up interacting more with each other when they are moving to random waypoints.



### Extension Results

For our extension we plan to do a parameter sweep on different values for platoons and squads for different types of movement. Currently we have the infrastructure built for a parameter sweep, and we just need to log all the data and visualize it. The paper never delved into the impacts of different sizes for platoons and squads on malware spread, meaning that this extension will give us a clear idea how size impacts mobile network infection rate. 

TODO: Try embedding animation

### Discussion

One continuing cause for concern is adapting the paper from Repast Simphony to repast4py, the Python library. As a result, we’ve done a lot of tuning, such as the times agents move on each step and the size of the infection area.

### Conclusion

### TODO
* Scale up squads for final figures
* Ensure tense matching
* Make ticks -> hours
* Fix methodology wording

### Annotated Bibliography

[1] [An agent-based modeling framework for cybersecurity in mobile tactical networks](https://journals.sagepub.com/doi/10.1177/1548512917738858) **Brian Thompson, James Morris-King** 
This paper investigates how malware infiltrates mobile tactical networks given different movement patterns and types of security forifications against mobile networks through agent based modeling. The paper highlights how even if different mobile networks may be isolated from others, lack of effective security policies coupled with different types of movement interactions can heavily impact malware spread behavior in the overall system.  
 
