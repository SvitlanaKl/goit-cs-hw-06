FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install pymongo
CMD ["python", "main.py"]
