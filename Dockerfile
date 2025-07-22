# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Expose Streamlit port
EXPOSE 8502

# Set environment variables for Streamlit
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8502

# Run the Streamlit app
CMD ["streamlit", "run", "streamlit_app_copy.py", "--server.port=8502", "--server.address=0.0.0.0"] 