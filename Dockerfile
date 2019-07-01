FROM python:3.6

ADD ./backend /app

WORKDIR /app
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 5000
CMD python app.py
