# 05 — Observability & Monitoring

> Stack covered: Splunk (primary), CloudWatch, Datadog, New Relic.
> Focused on the concepts EPAM asks and how to connect
> your real-world experience with the interview language.

---

## Index

1. [The 3 Pillars of Observability](#1-the-3-pillars-of-observability)
2. [Splunk — Your Primary Tool](#2-splunk)
3. [CloudWatch — AWS Native Stack](#3-cloudwatch)
4. [Datadog — Unified Observability](#4-datadog)
5. [New Relic — APM & Full-stack](#5-new-relic)
6. [Comparison Table: When to use each](#6-comparison-table)
7. [SLIs, SLOs, and Error Budget](#7-slis-slos-and-error-budget)
8. [Alerting: Design it right](#8-alerting-design-it-right)
9. [Interview Questions with Answer Key](#9-interview-questions)

---

## 1. The 3 Pillars of Observability

Before talking about tools, this is the conceptual framework you must master
for the interview. Everything Splunk, Datadog, CloudWatch, and New Relic
do fits into these three pillars:

```
┌─────────────────────────────────────────────────────────┐
│                   OBSERVABILITY                         │
├───────────────┬──────────────────┬──────────────────────┤
│    METRICS    │       LOGS       │       TRACES         │
│               │                  │                      │
│ How healthy   │ What exactly     │ Why did this         │
│ is the        │ happened and     │ request take         │
│ system?       │ when?            │ so long?             │
│               │                  │                      │
│ CPU, mem,     │ Events,          │ End-to-end request   │
│ error rate,   │ errors,          │ across               │
│ p99 latency   │ auditing         │ microservices        │
│               │                  │                      │
│ Splunk ITSI   │ Splunk Core      │ Splunk APM           │
│ CloudWatch    │ CloudWatch Logs  │ New Relic APM        │
│ Datadog       │ Datadog Logs     │ Datadog APM          │
│ New Relic     │ New Relic Logs   │ AWS X-Ray            │
└───────────────┴──────────────────┴──────────────────────┘
```

**The 4 Golden Signals** (Google SRE Book) — what you should always monitor:

| Signal | What it measures | Example Alert |
|--------|----------|-------------------|
| **Latency** | Response time (p50, p95, p99) | p99 > 500ms for 5 min |
| **Traffic** | Request volume | Drop > 50% vs baseline |
| **Errors** | Error rate (5xx, exceptions) | Error rate > 1% for 2 min |
| **Saturation** | How full the system is | CPU > 85% for 10 min |

> 💡 **In the interview**: When asked what you would monitor for a service,
> respond with the 4 golden signals. It's the answer senior engineers expect.

---

## 2. Splunk

### Why Splunk is your advantage in this interview

Splunk is the standard for large enterprises for log management and SIEM.
The fact that you've used it in production (dashboards, alerts, logs, APM)
puts you above most candidates who only know CloudWatch.

**How to present it in the interview**:
> *"My primary observability platform has been Splunk. I've built dashboards for
> golden signals monitoring, written SPL queries for incident investigation,
> configured alerts with on-call routing, and used Splunk APM for distributed
> tracing across microservices."*

---

### Splunk Architecture (to explain in interview)

```
Your apps / servers
        │
        │  (Universal Forwarder — lightweight agent)
        ▼
   Heavy Forwarder          ← parses, filters, routes
        │
        ▼
    Indexer(s)              ← stores and indexes data
        │
        ▼
   Search Head(s)           ← where you perform searches and build dashboards
```

In the cloud (Splunk Cloud): The architecture is the same but managed by Splunk.
In EKS: The Universal Forwarder runs as a DaemonSet (one pod per node).

---

### SPL — Search Processing Language

SPL is Splunk's query language. It works like a Unix pipeline:
each `|` passes the result to the next command.

```splunk
"Show error rate of the payments API in the last 15 minutes"

index=prod sourcetype=app_logs service=payments
| eval is_error = if(status_code >= 500, 1, 0)
| stats count as total, sum(is_error) as errors by _time span=1m
| eval error_rate = round((errors/total)*100, 2)
| timechart span=1m avg(error_rate) as "Error Rate %"
```

```splunk
"Top 10 slowest endpoints (p95 latency)"

index=prod sourcetype=nginx_access
| eval latency_ms = response_time * 1000
| stats perc95(latency_ms) as p95_latency by uri_path
| sort -p95_latency
| head 10
| rename uri_path as "Endpoint", p95_latency as "p95 Latency (ms)"
```

```splunk
"Detect anomalies: hosts with unusual error counts"

index=prod sourcetype=app_logs level=ERROR
| stats count as error_count by host, _time span=5m
| streamstats avg(error_count) as avg_errors stdev(error_count) as std_errors by host
| eval anomaly = if(error_count > avg_errors + (2 * std_errors), "YES", "NO")
| where anomaly="YES"
```

```splunk
"Correlate deploys with error spikes (for post-mortem)"

(index=prod sourcetype=app_logs level=ERROR)
OR
(index=ops sourcetype=deploy_events)
| eval event_type = if(sourcetype="deploy_events", "DEPLOY", "ERROR")
| timechart span=5m count(eval(event_type="ERROR")) as errors,
            count(eval(event_type="DEPLOY")) as deploys
```

### Alerting in Splunk

```
Splunk Alert Types:
1. Scheduled Alert  → Runs a search every X minutes, alerts if condition is met
2. Real-time Alert  → Continuous monitoring, more resource-intensive

Example of a well-configured alert:
- Search: error rate > 1% in a 5-minute window
- Schedule: Every 5 minutes
- Trigger condition: "Number of results > 0"
- Throttle: Don't alert more than once every 30 minutes (prevent alert fatigue)
- Action: PagerDuty webhook → on-call engineer
```

### Splunk APM (Distributed Tracing)

```
Splunk APM uses OpenTelemetry to instrument applications.

What you see in APM:
- Flame graph: Visualization of how much time each part of the request took
- Service map: Which services call which other services
- Error traces: Specific traces that ended in an error

Example to explain in an interview:
"We had an intermittent timeout in the checkout. Using Splunk APM, I found that
95% of the request time was spent in a call to the inventory service.
The flame graph showed it was a SQL query without an index. We resolved it in 20 minutes
thanks to the trace — without APM it would have taken hours of manual debugging."
```

---

## 3. CloudWatch

### Why it matters even if you use Splunk

CloudWatch is **AWS native**. Even if you use Splunk or Datadog as your primary platform,
CloudWatch remains important because:
- It's the default destination for Lambda, ECS, and EKS logs
- Auto Scaling alarms use CloudWatch metrics
- CloudTrail → CloudWatch Logs is the AWS auditing standard
- It doesn't require an agent for EC2, RDS, ALB metrics, etc.

### Key Components

```
CloudWatch
├── Metrics          → Time series data (CPU, memory, custom metrics)
├── Logs             → Log groups and streams
│   └── Logs Insights → Queries over logs (like SPL but more limited)
├── Alarms           → Alerts on metrics
├── Dashboards       → Visualization
└── Container Insights → Automatically collects EKS/ECS metrics and logs
```

### Metrics and Namespaces

```bash
# View available metrics for a service
aws cloudwatch list-metrics --namespace AWS/EC2

# Important Namespaces:
# AWS/EC2          → CPUUtilization, NetworkIn/Out, DiskRead/Write
# AWS/RDS          → DatabaseConnections, FreeStorageSpace, ReadLatency
# AWS/ApplicationELB → RequestCount, HTTPCode_Target_5XX_Count, TargetResponseTime
# AWS/EKS          → (basic, use Container Insights for details)
# ContainerInsights → pod_cpu_utilization, pod_memory_utilization
```

### CloudWatch Logs Insights — Basic Queries

```sql
-- Error rate in the last 30 minutes
fields @timestamp, @message
| filter @message like /ERROR/
| stats count(*) as error_count by bin(5m)
| sort @timestamp desc

-- Top IPs with most requests (nginx)
fields @timestamp, remoteAddr, request
| stats count(*) as request_count by remoteAddr
| sort request_count desc
| limit 20

-- Average latency per endpoint (API Gateway)
fields @timestamp, resourcePath, responseLatency
| stats avg(responseLatency) as avg_latency,
        percentile(responseLatency, 95) as p95_latency
        by resourcePath
| sort p95_latency desc
```

### Alarm Anatomy

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "api-high-error-rate" \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --dimensions Name=LoadBalancer,Value=app/my-alb/abc123 \
  --statistic Sum \
  --period 60 \           # Evaluation window: 1 minute
  --evaluation-periods 3 \  # Evaluate 3 consecutive periods
  --threshold 10 \          # If sum > 10 errors in 3 consecutive minutes
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123:my-alert \
  --ok-actions arn:aws:sns:us-east-1:123:my-alert    # Notify when resolved
```

### Container Insights on EKS

```bash
# Enable Container Insights
aws eks create-addon \
  --cluster-name my-cluster \
  --addon-name amazon-cloudwatch-observability

# Automatically available metrics:
# - pod_cpu_utilization       → CPU per pod
# - pod_memory_utilization    → Memory per pod
# - pod_network_rx_bytes      → Network ingress per pod
# - node_cpu_utilization      → CPU per node
# - cluster_failed_node_count → Failed nodes in cluster
```

---

## 4. Datadog

### Architecture on EKS

```
EKS Cluster
├── Datadog Agent (DaemonSet — one pod per node)
│   ├── Collects node metrics (CPU, memory, disk, network)
│   ├── Collects pod metrics (via kubelet)
│   ├── Tails container logs
│   └── APM traces (if app is instrumented)
└── Cluster Agent (Deployment — 1 replica)
    ├── Cluster metrics (events, deployment state)
    └── Autodiscovery (automatically detects services)
```

```bash
# Install Datadog with Helm
helm repo add datadog https://helm.datadoghq.com
helm install datadog-agent datadog/datadog \
  --namespace datadog \
  --create-namespace \
  --set datadog.apiKey=$DD_API_KEY \
  --set datadog.logs.enabled=true \
  --set datadog.apm.enabled=true \
  --set datadog.clusterAgent.enabled=true
```

### Key Datadog Concepts

**Tags**: The foundation of everything in Datadog. Every metric, log, and trace has tags.
```
host:web-01
env:production
service:payments
version:1.2.3
region:us-east-1
```
With these tags, you can filter any data: *"show me the error rate for the payments service
in production"* without writing a complex query.

**Monitors** (Alerts in Datadog):
```
Threshold Monitor  → Alerts if metric exceeds a fixed value
Anomaly Monitor    → Alerts if metric deviates from historical behavior
Forecast Monitor   → Alerts if metric is projected to cross a threshold in X hours
Composite Monitor  → Combines multiple monitors (alert if A and B are true)
```

**APM in Datadog**:
```
Service Map     → Dependency visualization between services
Flame Graph     → Breakdown of time within a request
Error Tracking  → Groups similar errors, shows trends
Continuous Profiler → CPU/memory at the code function level
```

**Dashboards**: Datadog has pre-designed dashboards for EKS, RDS, ALB, etc.
They can be imported with one click from the integrations catalog.

---

## 5. New Relic

### Main Differentiator

New Relic focuses on **APM and full-stack observability**.
Its agent is easy to install and provide deep application visibility
(transactions, SQL queries, external calls) with minimal configuration.

### Key Concepts

**New Relic APM**:
```
Transactions    → Response time per endpoint/method
Error rate      → % of transactions with errors per service
Throughput      → Requests per minute
Apdex score     → Satisfaction metric (0-1): what % of requests
                  were "satisfactory" (< T ms), "tolerating" (< 4T), or "frustrated"
Distributed tracing → End-to-end request tracing between services
```

**NRQL** — New Relic Query Language (SQL-like):
```sql
-- Error rate of payments service in the last hour
SELECT percentage(count(*), WHERE error IS true) as 'Error Rate'
FROM Transaction
WHERE appName = 'payments-service'
SINCE 1 hour ago
TIMESERIES 5 minutes

-- p95 latency per endpoint
SELECT percentile(duration, 95) as 'p95 Latency'
FROM Transaction
WHERE appName = 'api-gateway'
FACET request.uri
SINCE 30 minutes ago
LIMIT 20
```

**New Relic Alerts**:
```
Alert Policy  → Groups related alert conditions
Condition     → Defines when to trigger (threshold, anomaly, NRQL)
Notification  → Where the alert goes (PagerDuty, Slack, email)
```

---

## 6. Comparison Table

| | Splunk | CloudWatch | Datadog | New Relic |
|--|---|---|---|---|
| **Strength** | Log analytics, SIEM, compliance | Native AWS, zero friction | All-in-one, excellent UX | APM, easy instrumentation |
| **Logs** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Metrics** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **APM / Traces** | ⭐⭐⭐⭐ | ⭐⭐ (X-Ray) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Alerting** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cost** | High | Pay-per-use | High | High |
| **Learning Curve** | High (SPL) | Medium | Medium | Low |
| **Ideal for** | Enterprise, compliance | 100% AWS projects | Startups, SaaS, K8s | Apps with critical APM |

**When to recommend which in an interview**:
```
"For a 100% AWS project with no budget for external tools" → CloudWatch
"For a company with strict compliance (fintech, health, gov)" → Splunk
"For a team wanting an all-in-one platform with good UX" → Datadog
"For a team needing deep APM with minimal configuration" → New Relic
"In practice: CloudWatch for AWS infra metrics +
 Splunk/Datadog/New Relic for application observability" → More realistic answer
```

---

## 7. SLIs, SLOs, and Error Budget

### Definitions

```
SLI (Service Level Indicator)
→ The metric you measure. A number.
→ Example: "% of requests returning 2xx in less than 300ms"

SLO (Service Level Objective)
→ The target you set for that SLI. An internal commitment.
→ Example: "99.9% of requests must meet the SLI above"

SLA (Service Level Agreement)
→ The contract with the customer. Consequences if not met.
→ Example: "If availability < 99.5%, customer receives credit"

Error Budget
→ How much you can fail before breaking the SLO.
→ Example: SLO 99.9% → you can fail 0.1% = 43.8 min/month
```

### Error Budget Calculation

```
Period: 30 days = 43,200 minutes

SLO 99.9%:
  Error budget = 0.1% × 43,200 = 43.2 minutes/month of allowed downtime

SLO 99.5%:
  Error budget = 0.5% × 43,200 = 216 minutes/month (~3.6 hours)

SLO 99.99% ("four nines"):
  Error budget = 0.01% × 43,200 = 4.32 minutes/month
  (almost impossible to sustain without total automation)
```

### Good vs. Bad SLIs

```
❌ Bad SLI: "Server is up" (binary, doesn't reflect user experience)
❌ Bad SLI: "CPU < 80%" (resource metric, not experience metric)

✅ Good SLI: "% of requests with status 2xx or 3xx"
✅ Good SLI: "% of requests completed in < 500ms (measured at client)"
✅ Good SLI: "% of processing jobs completed successfully"
✅ Good SLI: "% of payment transactions processed without error"
```

### Burn Rate: What it is and how to alert

```
Burn rate = the speed at which you consume the error budget

Burn rate 1 = consuming budget exactly at the period's rhythm
  → You will exhaust the budget exactly on day 30

Burn rate 14.4 = consuming 14.4x faster than normal
  → You will exhaust the monthly budget in 2 days (30 / 14.4 = 2.08)

Burn rate alerting strategy (Google SRE):

┌─────────────────┬──────────────┬──────────────┬────────────────┐
│ Alert           │ Burn rate    │ Window       │ Budget consumed │
├─────────────────┼──────────────┼──────────────┼────────────────┤
│ Page (critical) │ > 14.4x      │ 1 hour       │ 2% in 1 hour   │
│ Page (critical) │ > 6x         │ 6 hours      │ 5% in 6 hours  │
│ Ticket (warning)│ > 3x         │ 3 days       │ 10% in 3 days  │
│ Ticket (warning)│ > 1x         │ 7 days       │ 10% in 7 days  │
└─────────────────┴──────────────┴──────────────┴────────────────┘
```

### What to do when the error budget is exhausted

```
1. Freeze all new feature deployments
   → Only allow stability and reliability fixes

2. Align product and technical teams:
   → The error budget is the objective reason (not an opinion) to stop features

3. Investigate what consumed the budget:
   → Was it an incident? → Post-mortem + action items
   → Was it an accumulation of small issues? → Reduce toil, improve tests

4. Review if the SLO is realistic:
   → If always exhausted, maybe the SLO is too aggressive for current architecture

5. Document in the Error Budget Policy (team document):
   → What happens when X% of budget is consumed
   → Who makes the decision to freeze features
```

---

## 8. Alerting: Design it right

### Alert Fatigue: The Main Enemy

```
Alert fatigue: When there are so many alerts (often false positives) that the team
starts ignoring or automatically silencing them.

Consequence: When a real critical alert arrives, no one attends to it.

Signs of alert fatigue in a team:
- Alerts are "commonly" triggered and left open
- Engineers silence alerts without investigating
- More alerts in an on-call shift than real incidents
- No one remembers why a certain alert exists
```

### Principles for Well-Designed Alerts

```
1. ACTIONABLE: Every alert must have a clear action
   ❌ Alert: "High CPU on some node"
   ✅ Alert: "Node web-03 CPU > 90% for 10 min — review K8s-NODE-CPU runbook"

2. URGENT: Only alert on things needing immediate attention
   ❌ Alert at 3 AM: "Disk usage > 70%"
   ✅ Alert at 3 AM: "Disk usage > 95% — system may run out of space in < 2h"

3. CONTEXT-RICH: Include all info to start investigating in the alert
   - Metric, value, threshold
   - Link to relevant dashboard
   - Link to runbook
   - Severity and expected response time

4. NO DUPLICATES: If 5 pods crash, 1 alert for "degraded deployment," 
   not 5 alerts for "pod crashed"
   → Use grouping in PagerDuty / OpsGenie

5. THROTTLED: Don't alert more than once every N minutes for the same issue
   → Splunk: throttle setting in the alert
   → Datadog: re-notify settings
```

### Severities (common standard)

| SEV | Description | Response Time | Example |
|-----|-------------|---------------------|---------|
| SEV1 | Total production impact, users affected | Immediate, 24/7 | API down, 100% error rate |
| SEV2 | Partial impact or severe degradation | < 30 min, 24/7 | 10% error rate, 5x latency |
| SEV3 | Minor degradation, workaround available | Business hours | Failed job, capacity alert |
| SEV4 | Informational, no current impact | Next sprint | Disk at 70%, cert expires in 30d |

---

## 9. Interview Questions

**"What are the 4 golden signals and why do they matter?"**

```
The 4 golden signals are the minimum monitoring framework for any service,
defined by the Google SRE Book:

1. Latency: How long it takes to respond. Not just the average — p99 is more
   representative as it shows the experience of the slowest 1% of users.

2. Traffic: How many requests it's processing. A sudden drop is as
   alarming as a spike — it might indicate users can't reach the service.

3. Errors: What % of requests fail. Monitoring only 5xx isn't enough —
   there are also "silent" errors (200 response with error in the body).

4. Saturation: How close the system is to its limit. CPU, memory,
   DB connections, queue size. Predicts issues before they happen.

Why they matter: They are technology-agnostic. The same 4 apply to a
REST API, a processing job, a database, or a streaming service.
They are the common language between SRE, DevOps, and development.
```

---

**"How do you investigate a sudden latency spike in production?"**

```
Structured process (what I do with Splunk or any tool):

1. SCOPE: Is it global or partial?
   → All endpoints or just one?
   → All users or just one region/ISP?
   → All nodes or just some?

   In Splunk:
   index=prod sourcetype=access_log
   | stats avg(response_time) by uri_path, datacenter
   | sort -avg(response_time)

2. TEMPORAL CORRELATION: When did it start exactly?
   → Coincide with a deploy? (look for deploy events in same timerange)
   → Coincide with a traffic spike?
   → Coincide with a config change?

3. DOWNSTREAM: Is the problem internal or a dependency?
   → APM / traces: which part of the request took the longest?
   → Flame graph: was it the DB? An external call? Serialization?

4. RESOURCES: Is there saturation?
   → CPU, memory, DB connections, thread pool exhaustion
   → In EKS: kubectl top pods, kubectl describe nodes

5. MITIGATE before root cause:
   → If a degraded service can be restarted or scaled, do it.
   → Deep investigation comes after service restoration.
```

---

**"How do you define an SLO for a new service?"**

```
4-step process:

1. Understand the user experience:
   "What makes this service considered 'working' for the user?"
   For a payments API: successful transaction processing in reasonable time.

2. Define the SLI (what to measure):
   - Availability: % of requests with 2xx or 3xx response
   - Latency: % of requests answered in < 500ms
   - Correctness: % of transactions processed without business error

3. Set the target (SLO) based on historical data:
   "If no history, start conservative (99%) and adjust over time."
   "If history exists, the SLO should be achievable but challenging."
   Never commit to more than current architecture can sustain.

4. Calculate error budget and set policy:
   SLO 99.5% → 3.6 hours error budget/month
   "If we consume > 50% of budget in the first week, we stop features."

Interview tip: Mention that SLOs are negotiated with product,
not defined by the technical team alone. It's a conversation about
what level of reliability is worth the engineering cost to achieve.
```

---

**"How do you reduce alert fatigue in a team with many noisy alerts?"**

```
Real experience you can share:

1. Audit: Review how many alerts from the last month had real action.
   If > 50% required no action → they are noise; delete or lower severity.

2. Group: Instead of one alert per crashed pod, one alert for degraded deployment.
   PagerDuty / OpsGenie have automatic grouping.

3. Adjust thresholds: Many alerts have over-sensitive thresholds.
   Adding evaluation periods (3 consecutive periods instead of 1)
   eliminates false positives from brief spikes.

4. Add throttle: If I already alerted for this issue, don't alert again
   for 30 minutes unless resolved and reappeared.

5. Runbooks for every alert: If an alert doesn't have a runbook, it shouldn't
   exist. The runbook defines what to do, and if the answer is "do nothing,"
   the alert isn't necessary.

6. Periodic review: Monthly 30-minute meeting where the team reviews
   top-firing alerts and decides to adjust, delete, or keep.
```

---

## 📖 Navigation

- **⬅️ Previous:** [04-cicd-concepts.en.md](./04-cicd-concepts.en.md) — CI/CD
- **➡️ Next:** [06-scripting-coding-prep.en.md](./06-scripting-coding-prep.en.md) — Scripting
- **🏠 Home:** [README.en.md](../README.en.md) — Documentation index
- **🔝 Back to top:** [00-concepts-overview.en.md](./00-concepts-overview.en.md) — Concept Map

---

## 🧪 Related Labs

Put these concepts into practice:

- **[Lab 07 — Prometheus + Grafana on EKS](../labs/lab-07-monitoring/Readme.md)**
  - Install kube-prometheus-stack with Helm
  - Create golden signals dashboards
  - Configure alerts with Alertmanager
  - Practice PromQL for SLOs and burn rates

- **[Lab 09 — CloudWatch Logs](../labs/lab-09-cloudwatch-logs/Readme.md)**
  - EC2 with JSON log generator
  - CloudWatch Agent for centralization
  - Metric Filters and Alarms
  - CloudWatch Logs Insights queries

- **[Scripting Lab — log_analyzer.py](../labs/scripting/README.md)**
  - Log analysis with Python
  - SLO and error budget calculation
  - Large file streaming

---

## 📖 Navigation

- **⬅️ Previous:** [04-cicd-concepts.en.md](./04-cicd-concepts.en.md) — CI/CD
- **➡️ Next:** [06-scripting-coding-prep.en.md](./06-scripting-coding-prep.en.md) — Scripting
- **🏠 Home:** [README.en.md](../README.en.md) — Documentation index
- **🔝 Back to top:** [00-concepts-overview.en.md](./00-concepts-overview.en.md) — Concept Map
