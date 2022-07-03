FROM frolvlad/alpine-python3:latest
EXPOSE 80
ADD chess/ /chess/
ADD requirements.txt /
RUN pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
CMD python -m chess