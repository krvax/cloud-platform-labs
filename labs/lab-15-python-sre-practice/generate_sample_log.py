#!/usr/bin/env python3
"""Generate a sample nginx access log for practice."""
import random
from datetime import datetime, timedelta

ENDPOINTS = [
    "/api/users", "/api/orders", "/api/health",
    "/api/payments", "/api/auth/login", "/api/products",
    "/api/search", "/api/notifications"
]
METHODS = ["GET", "POST", "PUT", "DELETE"]
IPS = [f"192.168.1.{i}" for i in range(1, 20)]
STATUS_CODES = [200]*70 + [201]*10 + [404]*5 + [500]*8 + [502]*4 + [503]*3

def generate_log(num_lines=1000, hours_back=2):
    """Generate realistic nginx log entries."""
    now = datetime.utcnow()
    lines = []

    for _ in range(num_lines):
        # Random timestamp within the last N hours
        offset = timedelta(seconds=random.randint(0, hours_back * 3600))
        timestamp = now - offset
        ts_str = timestamp.strftime("%d/%b/%Y:%H:%M:%S +0000")

        ip = random.choice(IPS)
        method = random.choice(METHODS)
        endpoint = random.choice(ENDPOINTS)
        status = random.choice(STATUS_CODES)
        size = random.randint(100, 50000)

        line = f'{ip} - - [{ts_str}] "{method} {endpoint} HTTP/1.1" {status} {size}'
        lines.append((timestamp, line))

    # Sort by timestamp
    lines.sort(key=lambda x: x[0])
    return [line for _, line in lines]


if __name__ == "__main__":
    log_lines = generate_log(num_lines=1000, hours_back=2)
    with open("sample_access.log", "w") as f:
        for line in log_lines:
            f.write(line + "\n")
    print(f"✅ Generated sample_access.log with {len(log_lines)} lines")
