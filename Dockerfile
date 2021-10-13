FROM ubuntu:18.04
RUN apt-get update && \
apt-get install -y software-properties-common && \
apt-add-repository universe && \
apt-get install -y python3-pip && \
apt-get install -y net-tools && \
apt-get install -y iproute2


#RUN pip3 install pandas && \
#pip3 install sqlalchemy && \
#pip3 install psycopg2 && \
#pip3 install elasticsearch


RUN mkdir mitm
WORKDIR mitm

RUN apt-get install -y python3-venv
RUN export PYTHONIOENCODING=utf8 && \
python3 -m pip install --user pipx && \
export PATH="$PATH:/root/.local/bin" && \
pipx ensurepath -f

RUN . ~/.bashrc && \
pipx install mitmproxy && \
pipx inject mitmproxy throttler
