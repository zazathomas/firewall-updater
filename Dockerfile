FROM python:3.13-alpine

# Set the maintainer
LABEL maintainer="Zaza Thomas"

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script into the container at /app
COPY update_firewall_rules.py /app/

# Run update_firewall_rules.py when the container launches
CMD ["python", "update_firewall_rules.py"]