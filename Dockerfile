FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt/ .
# RUN pip install -i https://mirror-pypi.runflare.com/simple -r requirements.txt
RUN pip install -r requirements.txt


# Copy project
COPY ./ .

# Create necessary directories
RUN mkdir -p static_volume media_volume logs

# Expose port
EXPOSE 8000

# Default command
CMD python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000
