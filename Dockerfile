# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose the port on which the app will run
EXPOSE 80

# Command to run the application
CMD ["python", "./app1.py"]
