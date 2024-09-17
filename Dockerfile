# Stage 1: Install dependencies
FROM python:3.10.0-alpine as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Create the final image with minimal size
FROM python:3.10.0-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . /app/

# Run data migration commands
RUN python manage.py checkdata || python manage.py loaddata files/gcc_gcp_pde_quiz_01.yaml
RUN python manage.py checkdata || python manage.py loaddata files/gcc_gcp_pde_quiz_02.yaml
RUN python manage.py checkdata || python manage.py loaddata files/gcc_gcp_pde_quiz_03.yaml
RUN python manage.py checkdata || python manage.py loaddata files/gcc_gcp_pde_quiz_04.yaml
RUN python manage.py checkdata || python manage.py loaddata files/gcc_gcp_pde_quiz_05.yaml
RUN python manage.py checkdata || python manage.py loaddata files/gcc_gcp_pde_quiz_06.yaml

# Run migrations
RUN python manage.py makemigrations
RUN python manage.py migrate

# Expose the port the app runs on
EXPOSE 8000

# Run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]

