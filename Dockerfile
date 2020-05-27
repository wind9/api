FROM python
MAINTAINER yunwei@ruitone.com.cn
COPY . /python
RUN pip3 install -r /python/requirements.txt
RUN rm /etc/timezone && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/timezone
WORKDIR /python
CMD ["python","run.py"]