FROM python:3-alpine3.11

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

# Expose the port the Flask app runs on
EXPOSE 5000

# Set the command to run the application
CMD python ./app.py
