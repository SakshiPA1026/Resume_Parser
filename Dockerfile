# Use an official Python runtime as a parent image
# We choose a Debian-based image as it's common and has apt for system packages.
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for spaCy and other packages
# python3-dev for Python header files
# build-essential for gcc and other compilation tools
# libblas-dev, liblapack-dev, libatlas-base-dev for BLIS/NumPy/SciPy optimization
# libpoppler-cpp-dev for PyMuPDF (if it has C++ dependencies)
# poppler-utils for pdfminer.six (if it needs command-line tools)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    libpoppler-cpp-dev \
    poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
# We use --no-cache-dir to save space in the Docker image
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy language model
RUN python -m spacy download en_core_web_sm

# Copy the rest of your application code into the container
COPY . .

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable inside the container
# This will be used by firebase-admin.
# The actual JSON content will be passed via Render's environment variables.
# This line just declares the variable; its value comes from Render.
ENV FIREBASE_CREDENTIALS_JSON=""

# Expose the port that Flask will run on (Gunicorn will use this)
# Render typically uses port 10000, but it's good practice to define it.
ENV PORT 10000
EXPOSE $PORT

# Command to run the application using Gunicorn
# app:app refers to the Flask app instance named 'app' in your 'app.py' file
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]
