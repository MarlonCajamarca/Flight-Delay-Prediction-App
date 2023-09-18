FROM python:3.10.13-slim

# Define the working directory inside container
WORKDIR /code

# Copy the requirements file to the working directory
COPY ./requirements-prod.txt /code/requirements.txt

# Install the requirements
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the app folder to the working directory
COPY ./challenge/api.py /code/app/api.py

# Copy the model folder to the working directory
COPY ./model/model.pkl /code/model/model.pkl

# Launch the app within container in port 80
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "80"]