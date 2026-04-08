# Hydroficient IoT Security Lab

This repository contains a sequence of Python projects (`Project3` through `Project8`) that progressively build an IoT telemetry pipeline and harden it against common cyber attacks (TLS/mTLS hardening, replay protection, and AI-based anomaly detection).

## Project Structure

- `Project3`: Baseline MQTT publisher/subscriber dashboard flow.
- `Project4`: TLS-enabled transport and certificate tooling/experiments.
- `Project5`: mTLS and identity/certificate test tooling.
- `Project6`: Replay attack simulation and rule-based defenses.
- `Project7`: Live security dashboard with replay defense events.
- `Project8`: AI-enhanced dashboard with anomaly scoring and attack simulation.
- `Notes`: Supporting documentation and references.

## Core Technologies

- Python 3.10+
- MQTT (`paho-mqtt`)
- WebSocket dashboard backend (`websockets`)
- ML utilities (`numpy`, `joblib`)
- X.509 certificate generation (`cryptography`)
- Mosquitto broker configs (`mosquitto_*.conf` in project folders)

## Quick Start

1. Install dependencies (see `requirements.txt`).
2. Ensure Mosquitto is installed locally.
3. Use certificates in each project's `certs` folder (or generate as directed in that project).
4. Run scripts from the specific project directory so relative cert paths resolve correctly.

Example:

```bash
cd Project8
python anomaly_injector.py
python subscriber_dashboard_ai.py
```

## Typical Workflow (Project8)

1. Start/configure Mosquitto with the matching `mosquitto_mtls.conf`.
2. Run `publisher_defended.py` (normal telemetry) or `anomaly_injector.py` / `attack_simulator.py` (security testing).
3. Run `subscriber_dashboard_ai.py` to validate messages and stream events to the dashboard.
4. Open `http://localhost:8000` to view live accepted/rejected/anomaly events.

## Notes

- Some projects reuse certificate bundles and shared secrets for lab/demo purposes.
- Keep test scripts and broker config aligned with the project version you are running.
- If an AI model file is required in `Project8`, place it as `anomaly_model.joblib`.
