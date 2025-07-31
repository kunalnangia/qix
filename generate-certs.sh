#!/bin/bash

# Create certs directory if it doesn't exist
mkdir -p nginx/certs

# Generate a private key
openssl genrsa -out nginx/certs/key.pem 4096

# Create a self-signed certificate
openssl req -new -x509 -key nginx/certs/key.pem -out nginx/certs/cert.pem -days 365 -subj "/CN=localhost"

echo "SSL certificates generated in nginx/certs/ directory."
echo "You may need to trust the self-signed certificate in your operating system."
