python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"