FROM python:3.9.0
# If needed you can use the official python image (larger memory size)
#FROM python:3.9.0

RUN mkdir /app/
WORKDIR /app

COPY src/hybridheatpumpservice ./src/hybridheatpumpservice
COPY pyproject.toml ./
COPY README.md ./
COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install ./

ENTRYPOINT python3 src/hybridheatpumpservice/hybrid_heatpump_service.py