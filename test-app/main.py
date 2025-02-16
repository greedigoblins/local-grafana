# Open Telemetry
import os
import logging
import time
import random
import uuid

from opentelemetry import trace, metrics

# Traces
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Logging
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry._logs import set_logger_provider

# Metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# General Otel Setup
name_salt = uuid.uuid4().hex[:6]
APP_SERVICE_NAME = f"py-demo-{name_salt}"
otel_resource = Resource.create(
    {
        SERVICE_NAME: APP_SERVICE_NAME,
        "service.instance.id": os.uname().nodename,
    }
)

if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", None) != None:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
        OTLPMetricExporter,
    )
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    tracing_endpoint = f"{endpoint}/v1/traces"
    metrics_endpoint = f"{endpoint}/v1/metrics"
    logs_endpoint = f"{endpoint}/v1/logs"
    trace_exporter = OTLPSpanExporter(endpoint=tracing_endpoint)
    metrics_exporter = OTLPMetricExporter(endpoint=metrics_endpoint)
    log_exporter = OTLPLogExporter(endpoint=logs_endpoint)

    print("Using remote telemetry")
    print(f"metrics_exporter: {metrics_endpoint}")
    print(f"trace_endpoint: {tracing_endpoint}")
    print(f"log_endpoint: {logs_endpoint}")
    print(f"service_name: {APP_SERVICE_NAME}")

else:
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter
    from opentelemetry.sdk._logs.export import ConsoleLogExporter
    from opentelemetry.sdk.metrics.export import ConsoleMetricExporter

    trace_exporter = ConsoleSpanExporter()
    log_exporter = ConsoleLogExporter()
    metrics_exporter = ConsoleMetricExporter()

# Trace Setup
trace_provider = TracerProvider(resource=otel_resource)

# Get a span_processor if you want to use the spans locally
# in our case its console logging.
span_processor = BatchSpanProcessor(trace_exporter)
# Add the span_processor to the tracer
trace_provider.add_span_processor(span_processor)
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

# Logging Setup
logger_provider = LoggerProvider(resource=otel_resource)
set_logger_provider(logger_provider)

log_record_processor = BatchLogRecordProcessor(log_exporter)
logger_provider.add_log_record_processor(log_record_processor)
otel_log_handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

# Metrics Setup
metric_reader = PeriodicExportingMetricReader(metrics_exporter, 1000, 500)
metrics_provider = MeterProvider(resource=otel_resource, metric_readers=[metric_reader])
metrics.set_meter_provider(metrics_provider)
metrics_meter = metrics.get_meter(APP_SERVICE_NAME)


work_counter = metrics_meter.create_counter(
    "py_work_counter", unit="1", description="Counts the amount of work done"
)


def main():
    logger = logging.getLogger()
    logger.addHandler(otel_log_handler)
    logger.setLevel(logging.INFO)
    logging.info(f"Starting the {APP_SERVICE_NAME} service")
    for i in range(100):
        with tracer.start_as_current_span("main") as span:
            span.set_attribute("loop_ip", f"{i}")
            logging.info(f"Doing the work {i}")
            work_counter.add(random.randint(1, 10), {"tatoes": "hobbit"})
            print("Do the work here")
        time.sleep(1)


if __name__ == "__main__":
    main()
