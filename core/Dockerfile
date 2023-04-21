FROM python:3.10.11-slim-bullseye
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt requirements.txt
RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt
WORKDIR /app
COPY . /app
# Run uvicorn under non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser
EXPOSE 1865
#CMD ["uvicorn", "cat.main:cheshire_cat_api", "--host", "0.0.0.0", "--port", "80", "--log-config", "./logger.yml"]
CMD ["uvicorn", "cat.main:cheshire_cat_api", "--log-config", "./logger.yml"]
