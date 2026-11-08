<!-- Imported from mukul975 (Apache-2.0) -->
# Command-Line Packet Inspection and Threat Hunting with TShark

---
name: threat-intel-tshark-packet-analysis
description: Automated command-line network packet analysis, payload extraction, protocol dissection, and anomaly hunting using TShark.
license: Apache-2.0
metadata:
  author: mukul975
  pack: threat-intel-url
---

# Performing Network Traffic Analysis with TShark

## Overview

This skill automates packet capture analysis using tshark (Wireshark CLI) and pyshark (Python wrapper). It extracts protocol distribution statistics, identifies suspicious network flows (port scans, beaconing, data exfiltration), extracts IOCs (IPs, domains, URLs), and detects DNS tunneling patterns from PCAP files.


## When to Use

- When conducting security assessments that involve performing network traffic analysis with tshark
- When following incident response procedures for related security events
- When performing scheduled security testing or auditing activities
- When validating security controls through hands-on testing

## Prerequisites

- tshark (Wireshark CLI) installed and in PATH
- Python 3.8+ with pyshark library
- PCAP or PCAPNG capture file for analysis

## Steps

1. **Extract Protocol Statistics** — Generate protocol hierarchy and conversation statistics from the capture
2. **Identify Top Talkers** — Rank source/destination IPs by volume and connection count
3. **Detect Suspicious Flows** — Flag port scanning patterns, unusual port usage, and high-frequency connections
4. **Extract Network IOCs** — Pull unique IPs, domains from DNS queries, and URLs from HTTP traffic
5. **Analyze DNS Traffic** — Detect DNS tunneling via high-entropy subdomain queries and excessive TXT records
6. **Generate Analysis Report** — Produce structured report with flow summaries and threat indicators

## Expected Output

- JSON report with protocol statistics and top talkers
- Suspicious flow detections with severity ratings
- Extracted IOCs (IPs, domains, URLs)
- DNS anomaly analysis results
