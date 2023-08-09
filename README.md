![This package is currently under development.](https://img.shields.io/badge/under-development-orange.svg)

This repository is under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)


Please contact alex@financial-portfolio.io for further information, for a demo or a collab.
</br>


### Tech Stack
<ul>
	<li>Deployment with AWS Beanstalk + Docker
	<li>DB: AWS RDS MySQL
	<li>Backend-server: Python-Flask
	<li>Frontend: HTML, CSS, Bootstrap, JavaScript, incl. JQuery and AJAX routines 
</ul>
<br>

**What does FP do?**  
- Connects to different market data API's. 
- Gathers and analyses the data through proprietary algoirthms. 
- Stores the raw data and results in remote AWS MySQL DB's.
- The app integrates a user authentication procedure.
- The signals yielded by the previous algorithms are displayed through an own developed frontend.


![alt text](SV/static/dash.png)


## "Data flow" view

![alt text](SV/static/signal_flow_na2.png)


<h4> To do: </h4>

NA <br>

<h2> Docker commands</h2> </br>
In the app folder, run the following command: </br>

Building the image:</br>
<code>docker build -t gts .</code><br>
<code>docker run gts</code>



### Testing

To run pytest, an all tests, at root dir type:<br>
<code>python -m pytest tests/</code> <br>

To run the main() at test_routes, without having an import error:<br>
<code>python -m tests.functional.test_routes</code>

