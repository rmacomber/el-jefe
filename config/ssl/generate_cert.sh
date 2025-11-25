#!/bin/bash
# SSL Certificate Generation Script
# For production use, use Let's Encrypt or purchase certificates

if [ ! -f "cert.pem" ]; then
    echo "Generating self-signed SSL certificate..."
    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes         -subj "/C=US/ST=State/L=City/O=ElJefe/CN=localhost"
    echo "Self-signed certificate generated successfully!"
else
    echo "Certificate already exists."
fi
