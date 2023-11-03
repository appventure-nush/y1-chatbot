FROM python:3.10-slim

# Install libraries
COPY ./requirements.txt ./
RUN pip cache purge
RUN pip install --no-cache-dir  -r requirements.txt && \
    rm ./requirements.txt

# Setup container directories
RUN mkdir /app

# Copy local code to the container
COPY ./app /app

# launch server with gunicorn
WORKDIR /app
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]