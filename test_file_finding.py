#!/usr/bin/env python3
"""Test biometric file finding."""

from csv_api_sender import BiometricAPIProcessor

# Create processor with sample biometric directory
processor = BiometricAPIProcessor(
    api_base_url="http://192.168.0.7:4000",
    biometric_dir="/home/acsun-arch/Projects/FireFighter/sample_biometric_data"
)

# Test finding files for license number
numero_carta = "10028588"
print(f"Looking for biometric files for license: {numero_carta}")
print(f"Biometric directory: {processor.biometric_dir}")
print()

file_mapping = processor.find_biometric_files(numero_carta)

if file_mapping:
    print(f"✓ Found {len(file_mapping)} file(s):")
    for api_field, file_path in file_mapping.items():
        print(f"  - {api_field:20} → {file_path}")
else:
    print("✗ No files found")

# Test building payload
print("\nBuilding payload...")
payload = processor.build_payload_from_license_number(numero_carta)

if payload:
    print(f"✓ Payload has {len(payload)} field(s):")
    for field, data in payload.items():
        print(f"  - {field:20} → {len(data)} bytes (base64)")
else:
    print("✗ Empty payload")
