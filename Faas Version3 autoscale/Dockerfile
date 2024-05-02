
FROM python:3.9-slim
WORKDIR /
COPY . ./
RUN apt update
RUN pip install --upgrade pip
RUN pip install -r requirement.txt
EXPOSE 8000
CMD ["python", "manage.py", "runserver","0.0.0.0:8000"]
