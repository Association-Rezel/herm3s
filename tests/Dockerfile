# Use a base image
FROM alpine:latest


# Install necessary dependencies
RUN apk update && apk add --no-cache bash && apk add --no-cache curl && apk add --no-cache jq

# Copy the script to the container
COPY unit_tests.sh .

# Make the script executable
RUN chmod +x unit_tests.sh

# Run the script when the container starts
CMD ["./unit_tests.sh"]