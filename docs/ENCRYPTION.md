# Encryption (PRD FR9)

## At rest (AES-256)

Sensitive fields are encrypted before being stored in PostgreSQL when a key is configured.

- **Algorithm:** AES-256-GCM (authenticated encryption).
- **Configuration:** Set `DATA_ENCRYPTION_KEY` in the environment to a **base64-encoded 32-byte key**.
  - Generate one: `python -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode())"`
- **Fields encrypted:**  
  - `scenarios.input_description`  
  - `audit_log.details`
- **Behavior:** If `DATA_ENCRYPTION_KEY` is not set or invalid, values are stored and read in plaintext (backward compatible). Existing plaintext rows remain readable.

## In transit

Encryption in transit is handled by the deployment environment, not the application.

- **Production:** Use **HTTPS/TLS** (e.g. reverse proxy with TLS termination, or TLS on the app server) so all client–server traffic is encrypted.
- The app does not implement TLS itself; it is a deployment/infrastructure concern.
