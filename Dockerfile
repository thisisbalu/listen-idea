# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose any necessary ports (optional, depending on your app)
# EXPOSE 8080

# Set environment variables (optional, if needed for your script)
# ENV VAR_NAME=value

# Run the script when the container launches
CMD ["python", "main.py"]
