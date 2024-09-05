# Use the Python 3.9 slim base image
FROM public.ecr.aws/docker/library/python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application code into the container
COPY app.py ./

# Expose the port that Streamlit will run on (default is 8501)
EXPOSE 8501

ENTRYPOINT ["streamlit"]

# Set the command to run the Streamlit application
CMD ["run","app.py"]