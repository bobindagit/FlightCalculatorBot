FROM python:3.10.0
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /working/FlightCalculatorBot

COPY requirements.txt /working/FlightCalculatorBot/
RUN pip install --no-cache-dir -r /working/FlightCalculatorBot/requirements.txt

COPY . /working/FlightCalculatorBot

CMD ["python", "-u", "main.py"]