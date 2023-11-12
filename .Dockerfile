FROM python:3.11.4-bookworm

RUN pip install --upgrade pip

WORKDIR /root/code

RUN pip install flask
RUN pip install numpy
RUN pip install mlflow
RUN pip install seaborn
RUN pip install matplotlib
RUN pip install scikit-learn
RUN pip install ppscore
RUN pip install pytest

COPY code/ /root/code/


CMD tail -f /dev/null