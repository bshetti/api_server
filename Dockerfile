FROM alpine:latest
MAINTAINER Bill Shetti "billshetti@gmail.com"
WORKDIR /app
ADD . /app
ENV MYSQL_ID="db_app_user" 
ENV MYSQL_PASSWORD="VMware123!" 
ENV MYSQL_SERVER="fitcyclecustomers.cy4b7ufzt54x.us-west-2.rds.amazonaws.com"
 
RUN apk update && \
    apk add mysql mysql-client && \
    apk add py-pip && \
    apk add py-sqlalchemy && \
    apk add py-flask && \
    apk add py-mysqldb && \
    apk add py-requests

COPY entrypoint/docker-entrypoint.sh /usr/local/bin/
RUN chmod 777 /usr/local/bin/docker-entrypoint.sh
RUN ln -s /usr/local/bin/docker-entrypoint.sh /app # backwards compat

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["docker-entrypoint.sh"]
#CMD ["python", "api_server.py"]
