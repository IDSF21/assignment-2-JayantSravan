# Pittsburgh Port Authority On-time Performance (OTP)

## Application Link: https://share.streamlit.io/jayantsravan/assignment-2-jayantsravan/main/application.py

## 1. Goals of the project

A city's public transportation system is a testament to how well the city is planned. Pittsburgh is famous for its efficient, well-connected, and punctual public transportation system. As an intrigued visitor to this city, I wanted to understand (and also let the users visualize) using data how well this claim holds.

**The goal of this project is to give the user an understanding of the distribution of On-time Performance of Pittsburgh Port Authority transit vehicles over time and locations in the city.** A transit vehicle is said to be on time if it reaches a given destination within one minute of its scheduled time. The questions asked would be:

a. How is the OTP distributed geographically in the city?

b. How has the OTP varied in the past?

Both of the above questions tweaked to a desired granularity using filters.

To my surprise, data suggested that Pittsburgh public transit has remarkable punctuality (atleast towards the center of the city). And they have been very consistent about this throughout the past 3 years and across the garages.

I have baked in 'Will my transit be on time?' functionality in the application. Hope this helps some users be informed about any possible delays.

## 2. Design choices

### a. Geographical distribution

I have decided to go with a pydeck interactive map visualization using hexagon layers to depict OTPs. Hexagon layers were used because of how well they use the third dimension of the map to encode a bounded numerical datapoint. They are easy to interpret and allow panning and zooming. I have used a column layer to depict the garage locations for reference.

Pydeck heatmaps were a possible alternative to this. They encode numerical data in color and make the graph look cleaner. But the problem with pydeck's heatmaps was that they were slow to respond to interactions like zooming and panning. Also, they do not engage as well a hexagonal layer in general because of lack of a third dimension.

### b. Time distribution

I have decided to go with a line chart offered by streamlit for this. This was a pretty easy decision as this was a time series data and nothing depicts the trends in a time series as well as a line chart to a common user.

Seaborn/Matplotlib line chart were a possible alternative to this but they are simply not as good looking (without any design changes)/ polished as the integrated line charts of streamlit.

### c. Will my transit be on time?

I have to give credit to the streamlit implementation of metrics component. It is a well thought out offering which looks good and is useful in many scenarios. This component inspired this particular module of my application. Hence, it was an obvious choice for this encoding.

## 3. Development Process

This is a solo project. I spent approximately 15 hours on this project.

Most of the time was spent on learning the streamlit framework by experimenting with the demo codes provided by streamlit. I also spent a significant amount of time discussing with some friends and relatives about what datasets I could consider to ask an interesting question. Fortunately, I stumbled across these datasets when I was looking to find some data about the city I live in.

### Here is a split of the time taken in each task:

a. Learning streamlit and experimentation - 3 hours

b. Exploring the datasets and selecting one (two, in my case) - 4 hours

c. Experiementing with pydeck - 2 hours

d. Writing the application - 5 hours

e. Figuring out deployment - 1 hour

### Other interesting questions I was considering:
a. Is there correlation between the income of a particular location in Pittsburgh and the proportion of people from a particular ethnicity living in there? I explored census datasets extensively for this.
b. Is there a correlation between OTP of the transit system in a region and the income of the people living there?

