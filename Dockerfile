# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Added --no-cache-dir to keep the image size small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code associated with the user request
COPY . .

# Expose port 8080 for Streamlit
EXPOSE 8080

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
