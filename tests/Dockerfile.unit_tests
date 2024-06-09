# Use a base image
FROM alpine:latest


# Install necessary dependencies
RUN apk update && apk add --no-cache bash && apk add --no-cache curl && apk add --no-cache jq && apk add dos2unix

# Copy the script to the container
COPY unit_tests.sh .

COPY test_ac2350_defaultConfigfile.txt .
COPY test_ac2350_configfile.txt .

# Make the script executable
RUN chmod +x unit_tests.sh
RUN dos2unix unit_tests.sh
RUN dos2unix test_ac2350_defaultConfigfile.txt
RUN dos2unix test_ac2350_configfile.txt


# Run the script when the container starts
CMD ["./unit_tests.sh"]
# CMD ["sleep", "infinity"]