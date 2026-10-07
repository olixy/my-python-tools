# my-python-tools

Personal Python utilities, installable as a local package via `uv add --editable /path/to/my-python-tools`.

## Tools

- **email_sender** — send transactional emails via Brevo or Gmail SMTP. Credentials are loaded automatically from `src/my_python_tools/.env` (copy `.env.example` to get started).

## Usage

```python
from my_python_tools.email_sender import send_email

send_email("you@example.com", "Subject", "Body")
```
