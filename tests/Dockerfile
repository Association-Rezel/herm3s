# Use a base image
FROM alpine:latest


# Install necessary dependencies
RUN apk update && apk add --no-cache bash && apk add --no-cache curl && apk add --no-cache jq && apk add dos2unix

# Copy the script to the container
COPY unit_tests.sh .

COPY defaultConfigfile.txt .
COPY configfile.txt .

# Make the script executable
RUN chmod +x unit_tests.sh
RUN dos2unix unit_tests.sh


# Run the script when the container starts
CMD ["./unit_tests.sh"]
# CMD ["sleep", "infinity"]