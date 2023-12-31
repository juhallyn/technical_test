FROM python:3.12

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in Pipfile
RUN pip install pipenv
RUN pipenv install --deploy

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME RPN

# Run app when the container launches
CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
