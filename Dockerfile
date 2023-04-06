FROM python:3.8.0-slim
LABEL maintainer alexnesovic@getthesignals.com

ENV aws_db_endpoint=flaskfinance.ccxri6cskobf.eu-central-1.rds.amazonaws.com
ENV aws_db_pass=awsaws1010
ENV aws_db_user=ubuntu

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean
COPY requirements.txt /app/requirements.txt
WORKDIR app
RUN pip install --upgrade pip
RUN pip install --user -r requirements.txt
COPY . /app

ENV FLASK_ENV development
EXPOSE 5000
CMD ["python","app.py"]