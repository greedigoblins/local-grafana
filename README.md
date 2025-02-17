# Local Grafana

A setup of the Loki, Tempo, Mimir and Grafana (LGTM) Stack.

We have replaced mimir with the far easier to locally host Prometheus.
We have also added Alloy as an aggregator.

This should give you everything you need to get running with local Open Telemetry.

There is currently a Docker Compose version. However we will also get a kubernetes version running.


# Docker compose

To use the docker compose version you will need a recent version of docker installed.
Docker now comes with compose built in. I'd recommend docker desktop since it is
built to be easy.

Firstly you will need to cd to the docker-compose directory: `cd docker-compose`.

Start all the containers via `docker compose up`.

You can now send open telemetry data in via `http://localhost:4317` via gRPC.

You can get to Grafana on `http://localhost:3001`. You will not need to authenticate.
The data sources will also be present already. So you just need to create your dash boards.

If you are working with this a lot, I would recommend exporting your dashboards.
