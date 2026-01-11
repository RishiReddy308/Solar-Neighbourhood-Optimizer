# Solar Panel Electricity Usage Time Optimizer

This project is for tracking a solar panelled homes electricity demand compared to the electricity it produces from the panels. A static website is updated automatically once a day at midnight to display a graph of the latest forecast of the next 7 days.

https://rishireddy308.github.io/Solar-Panel-Electricity-Usage-Time-Optimizer/

<img width="2220" height="1239" alt="image" src="https://github.com/user-attachments/assets/d5550359-f6a4-486e-b9ce-c76907c78508" />

# How it is made

I used an open-meteo API  to get temperature and shortwave radiation data. Then 2 functions were called to determine solar energy produced and the houses demand. I used pandas to store the information and plotly to make the graphs. Github actions was used to run the script every day at midnight and update the static page displaying the graph.

# What I learned

I learned a lot of about github actions and automation, including how to write a yaml file. I also learned about DataFrames with Pandas.



