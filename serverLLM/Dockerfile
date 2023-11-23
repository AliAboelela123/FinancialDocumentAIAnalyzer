# Use an official Python runtime as a parent image
FROM python:3.9-slim
ENV OPENAI_API_KEY XXX

# Copy the entire serverLLM directory into the container
COPY ./serverLLM /usr/src/app/serverLLM

# Set the working directory to the serverLLM directory
WORKDIR /usr/src/app/serverLLM

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5001

# Run server.py when the container launches
CMD ["python", "server.py"]
