FROM python
MAINTAINER yunwei@ruitone.com.cn
COPY . /python
RUN pip3 install -r /python/requirements.txt
WORKDIR /python
CMD ["python","run.py"]