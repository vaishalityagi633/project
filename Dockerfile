# Use an official Python runtime as a parent image
FROM python:3.12-slim
# Install ODBC driver and dependencies
RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*
# Install SQL Server client tools
#RUN apt-get update && apt-get install -y curl gnupg && \
    #curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    #curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    #apt-get update && ACCEPT_EULA=Y apt-get install -y mssql-tools unixodbc-dev


# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Use an existing SQL Server image as the base image


# Set environment variables for database name and credentials
ENV MSSQL_DB=PROJECT
ENV MSSQL_DB_USER=vaishali
ENV MSSQL_DB_PASSWORD=librarymgmt2393
ENV MSSQL_HOST=host.docker.internal
ENV MSSQL_PORT=1433


# Expose the port Flask runs on
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py
# Start SQL Server when the container starts
#CMD ["/opt/mssql/bin/sqlservr"]
# Run app.py when the container launches
CMD ["python", "app.py", "--host=0.0.0.0","--port=5000"]





