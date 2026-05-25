#!/usr/bin/env python3
"""
Exercise 1: SRE Log Analyzer
=============================
SCENARIO: You're on-call, get paged for elevated 5xx errors.
TASK: Find top 5 endpoints with most 5xx errors in the last hour.

This is how you'd solve it in an interview — step by step, talking out loud.
"""

# =============================================================================
# STEP 0: Imports — always start here
# =============================================================================
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# =============================================================================
# STEP 1: Define the regex pattern for nginx combined log format
#
# Interview talk: "First, I need to parse the log format. Nginx combined
# format has: IP, timestamp, method, path, status code, and size.
# I'll use a regex to extract what I need."
# =============================================================================

# Nginx log format:
# 192.168.1.1 - - [18/May/2026:17:45:23 +0000] "GET /api/users HTTP/1.1" 500 1234

LOG_PATTERN = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+)'       # IP address
    r'.*?'                                 # skip to timestamp
    r'\[(?P<timestamp>[^\]]+)\]'           # [timestamp]
    r'\s+"(?P<method>\w+)'                 # "METHOD
    r'\s+(?P<endpoint>\S+)'                # /path
    r'\s+HTTP/\d\.\d"'                     # HTTP/1.1"
    r'\s+(?P<status>\d{3})'                # status code
)

# Nginx timestamp format
TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


# =============================================================================
# STEP 2: Parse a single line
#
# Interview talk: "I'll create a function to parse one line. If the line
# doesn't match the pattern, I'll skip it gracefully — production logs
# can have malformed lines."
# =============================================================================

def parse_line(line):
    """Parse a single nginx log line. Returns dict or None if malformed."""
    match = LOG_PATTERN.search(line)
    if not match:
        return None

    return {
        "ip": match.group("ip"),
        "timestamp": datetime.strptime(match.group("timestamp"), TIME_FORMAT),
        "method": match.group("method"),
        "endpoint": match.group("endpoint"),
        "status": int(match.group("status")),
    }


# =============================================================================
# STEP 3: Filter by time window and error status
#
# Interview talk: "Now I need to filter: only 5xx errors, only last hour.
# I'll stream the file line by line so it works on large files too."
# =============================================================================

def get_recent_errors(filepath, hours=1):
    """
    Stream log file, yield only 5xx errors from the last N hours.
    Memory efficient — works on 100GB files.
    """
    cutoff = datetime.now().astimezone() - timedelta(hours=hours)

    with open(filepath, 'r') as f:
        for line in f:  # Streams line by line — constant memory
            parsed = parse_line(line)
            if parsed is None:
                continue
            # Filter: only 5xx AND within time window
            if parsed["status"] >= 500 and parsed["timestamp"] >= cutoff:
                yield parsed


# =============================================================================
# STEP 4: Aggregate — count errors per endpoint + calculate error rate
#
# Interview talk: "I'll count errors per endpoint using Counter, and also
# track total requests per endpoint to calculate error rate."
# =============================================================================

def analyze_errors(filepath, hours=1, top_n=5):
    """
    Main analysis function.
    Returns top N endpoints by 5xx error count with error rates.
    """
    # We need two passes for error rate... OR we can do it in one pass
    # by tracking both total and errors per endpoint
    endpoint_errors = Counter()
    endpoint_total = Counter()

    cutoff = datetime.now().astimezone() - timedelta(hours=hours)

    with open(filepath, 'r') as f:
        for line in f:
            parsed = parse_line(line)
            if parsed is None:
                continue

            # Only count requests within our time window
            if parsed["timestamp"] >= cutoff:
                endpoint_total[parsed["endpoint"]] += 1

                if parsed["status"] >= 500:
                    endpoint_errors[parsed["endpoint"]] += 1

    # Build results with error rate
    results = []
    for endpoint, error_count in endpoint_errors.most_common(top_n):
        total = endpoint_total[endpoint]
        error_rate = (error_count / total * 100) if total > 0 else 0
        results.append({
            "endpoint": endpoint,
            "errors": error_count,
            "total_requests": total,
            "error_rate": round(error_rate, 2),
        })

    return results


# =============================================================================
# STEP 5: Pretty print the results
#
# Interview talk: "Finally, I'll format the output so it's actionable
# for the on-call engineer."
# =============================================================================

def print_report(results, hours=1):
    """Print a formatted incident report."""
    print(f"\n{'='*60}")
    print(f"🚨 5xx ERROR REPORT — Last {hours} hour(s)")
    print(f"{'='*60}")
    print(f"{'Endpoint':<30} {'Errors':>8} {'Total':>8} {'Rate':>8}")
    print(f"{'-'*30} {'-'*8} {'-'*8} {'-'*8}")

    for r in results:
        severity = "🔴" if r["error_rate"] > 10 else "🟡" if r["error_rate"] > 5 else "🟢"
        print(f"{severity} {r['endpoint']:<28} {r['errors']:>8} {r['total_requests']:>8} {r['error_rate']:>7}%")

    print(f"{'='*60}")

    if results:
        worst = results[0]
        print(f"\n⚠️  WORST: {worst['endpoint']} — {worst['errors']} errors ({worst['error_rate']}% error rate)")
        print(f"   ACTION: Check this endpoint's dependencies (DB, external APIs, memory)")


# =============================================================================
# STEP 6: Main — tie it all together
# =============================================================================

if __name__ == "__main__":
    import sys
    import os

    # Generate sample log if it doesn't exist
    log_file = "sample_access.log"
    if not os.path.exists(log_file):
        print("📝 Generating sample log file...")
        from generate_sample_log import generate_log
        lines = generate_log(num_lines=1000, hours_back=2)
        with open(log_file, "w") as f:
            for line in lines:
                f.write(line + "\n")
        print(f"✅ Generated {log_file}")

    # Run analysis
    results = analyze_errors(log_file, hours=2, top_n=5)
    print_report(results, hours=2)

    # Bonus: show what you'd do next in production
    print("\n📋 NEXT STEPS (what I'd tell the team):")
    print("   1. Check if a recent deploy correlates with the spike")
    print("   2. Look at dependency health (RDS, Redis, external APIs)")
    print("   3. Check if HPA is scaling — are pods OOMKilled?")
    print("   4. Review error logs for stack traces on the worst endpoint")
