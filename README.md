![This package is currently under development.](https://img.shields.io/badge/under-development-orange.svg)

Please contact alex@financial-portfolio.io for further information, for a demo or a collab.
</br>

<ul>
	<li>Deployment with AWS Beanstalk + Docker
	<li>DB: AWS RDS MySQL
	<li>Backend-server: Python-Flask
	<li>Frontend: HTML, CSS, Bootstrap, JavaScript, incl. JQuery and AJAX routines 
</ul>
<br>

**What does it do?**
Connects to different market data API's. Gathers and synthetizes the data. Will synthesize and display the competitive arenas for every chosen stock.
The app integrates a user authentication procedure.


![alt text](SV/static/dash.png)


## "Data flow" view

![alt text](SV/static/signal_flow_na2.png)


<h4> To do: </h4>


<h4> Command to create virtual env (VS code, Ubuntu 20) </h4>
<p>In <strong>project root dir</strong> open command line:</p>

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

