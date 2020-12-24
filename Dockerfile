FROM ubuntu:latest

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update --fix-missing -y

RUN apt-get install git-all -y
RUN git clone https://github.com/CorgiTeamIncorporated/FiltItBot.git
COPY config.py /FiltItBot/config.py
WORKDIR /FiltItBot

RUN apt-get install -y python3-pip python-dev build-essential
RUN pip3 install pyTelegramBotAPI
RUN pip3 install scikit-image

CMD python3 main.py