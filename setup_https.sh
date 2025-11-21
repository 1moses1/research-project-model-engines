#!/bin/bash

# Setup HTTPS/TLS for Phase 2.5 Model API
# Generates self-signed certificate for development/staging

echo "========================================================================"
echo "HTTPS/TLS SETUP FOR PHASE 2.5 MODEL"
echo "========================================================================"
echo ""

cd "$(dirname "$0")"

# Create certs directory
mkdir -p certs
cd certs

echo "Step 1: Generating private key (2048-bit RSA)..."
openssl genrsa -out server.key 2048
echo "  ✅ Private key generated: certs/server.key"
echo ""

echo "Step 2: Generating certificate signing request..."
openssl req -new -key server.key -out server.csr \
    -subj "/C=RW/ST=Kigali/L=Kigali/O=Rwanda SOC/OU=Compliance Monitoring/CN=localhost"
echo "  ✅ CSR generated: certs/server.csr"
echo ""

echo "Step 3: Generating self-signed certificate (365 days validity)..."
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
echo "  ✅ Certificate generated: certs/server.crt"
echo ""

echo "Step 4: Setting secure permissions..."
chmod 400 server.key
chmod 444 server.crt server.csr
echo "  ✅ Permissions set (key: 400, cert: 444)"
echo ""

echo "========================================================================"
echo "HTTPS/TLS SETUP COMPLETE ✅"
echo "========================================================================"
echo ""
echo "Generated Files:"
echo "  - certs/server.key (Private key - KEEP SECURE)"
echo "  - certs/server.crt (Certificate)"
echo "  - certs/server.csr (Certificate signing request)"
echo ""
echo "Certificate Details:"
openssl x509 -in server.crt -noout -subject -dates
echo ""
echo "⚠️  WARNING: This is a SELF-SIGNED certificate for development/staging"
echo ""
echo "For Production:"
echo "  1. Use Let's Encrypt: certbot certonly --standalone -d yourdomain.com"
echo "  2. Or use your organization's Certificate Authority"
echo ""
echo "To use with Flask API:"
echo "  app.run(ssl_context=('certs/server.crt', 'certs/server.key'))"
echo ""
echo "========================================================================"
