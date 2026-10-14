FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY mcp_server.py policy_loader.py policy_search.py ./
COPY data/policies.json ./data/policies.json

CMD ["python", "mcp_server.py"]