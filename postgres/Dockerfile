FROM postgres:10.1
RUN localedef -i ja_JP -c -f UTF-8 -A /usr/share/locale/locale.alias ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
COPY ./db/init.sql /docker-entrypoint-initdb.d/