---
card-type: platform-thesis
card-id: store-network-integrity
card-version: 1
domain: platform
layer: cross-cutting
status: draft
tags: [VSM, store-brain, network-security, device-registry, device-manifest, threat-detection, compliance, SOX, PII, HIPAA, GDPR, card-skimmer, rogue-AP, SMB, LP]
last-compiled: 2026-04-29
---

## What this is

The store integrity monitoring capability: the VSM (store brain / Virtual Store Manager) as both process orchestrator and continuous security sensor. The premise is that the store's physical and digital state — transaction events, inventory positions, chain entry sequence, network device presence — should all be visible to the VSM in real time, and deviations from known-good state should generate signals before they become losses.

For SMB retailers specifically, this addresses a gap that no current platform fills: the retailer doesn't know what devices are on their network, doesn't know if their router has default credentials, doesn't know if a vendor's laptop is still connected three days after the service visit. The VSM makes this observable.

## The device manifest

Every store has a manifest: the enumerated set of devices that belong on that store's network, their MAC addresses, their device type classification, their last-seen timestamp, and their expected behavioral profile. The manifest is a site-level configuration entity in the merchant namespace — the same namespace hierarchy that holds PO records and chain events.

**Known devices:**
- POS terminals (classified by model and registered serial)
- Network switches and routers (registered MAC, expected firmware version)
- Security and LP cameras (registered MAC, expected subnet)
- Handheld scanners and receiving devices (registered MAC, assigned to dock door or LP badge)
- Manager and field operative mobile devices (registered by authenticated user credential)
- Vendor-managed devices (registered with expected visit window — departure timestamp expected)

**Manifest management:** the VSM maintains the manifest as a live data structure. New devices are not auto-added — they trigger an unknown device alert and require manual registration before they are added to the manifest. Any device that was registered but has been absent for more than its expected reconnect window triggers a missing device alert (theft signal, hardware failure signal).

## Continuous network monitoring

The VSM runs continuous DHCP lease monitoring and ARP table scanning against the store's network. Every device presence event — new connection, reconnection, extended absence — is evaluated against the manifest:

- **Known device, expected behavior:** logged, no alert
- **Known device, anomalous behavior:** behavior anomaly alert (e.g., POS terminal initiating outbound connections on non-POS ports — card skimmer behavior pattern)
- **Unknown device:** immediate alert — device type attempted by fingerprint (OS, port profile, traffic pattern), alert routed to LP and store manager
- **Vendor device past expected departure window:** escalating alert — first alert to store manager, second to district LP

**Card skimmer detection pattern:** a new device appears in physical proximity to a POS terminal and begins appearing on the network at the same MAC address range as known POS hardware, or appears on the network but shows traffic patterns inconsistent with POS (non-payment-protocol outbound, high-frequency small packet bursts). This behavioral fingerprint is a known skimmer pattern. The VSM flags it immediately.

**Rogue access point detection:** a new device presents as a Wi-Fi access point (detected via beacon frames or DHCP requests consistent with AP behavior). Any AP not in the manifest is a rogue AP — either a threat device or an employee hotspot. Both are alerts.

**Default credential risk:** the VSM periodically checks registered network infrastructure devices (routers, switches) against the known-default-credential database for their manufacturer and model. A device with known-default credentials flagged and escalated to the operator — this is a configuration failure, not an attack, but it is a material vulnerability that the SMB operator almost certainly does not know exists.

## The VSM as security sensor

The VSM monitors itself as rigorously as it monitors the store. Self-monitoring indicators:

- **Chain entry rate:** the VSM tracks its own event write rate by event type and by operative. A store with no receiving discrepancy events during a receiving shift is either receiving perfectly (possible) or the capture tool is broken or not being used (more likely). Either condition generates a signal to the Operations Agent.
- **Sequence integrity:** the VSM monitors the chain sequence for its merchant namespace. A gap in sequence numbers is not a normal condition — it indicates a write failure, a network interruption that wasn't handled by the queue, or active suppression of events. Any gap generates an immediate integrity alert.
- **Write latency:** the VSM tracks its own latency from event confirmation to chain entry. A latency spike (above the 5-second field capture SLA, or above the 2-second MCP write SLA) indicates infrastructure degradation or an active load condition. Sustained latency above threshold escalates to the Operations Agent.
- **POS write path queue depth:** if the local POS queue (the 24-hour buffer that holds events when the network is down) begins filling, the VSM alerts before the buffer approaches capacity. A full buffer means events are queuing but not being flushed — the chain is behind real time.

## Compliance monitoring

The compliance monitoring agent runs as an event stream subscriber. It does not gate transactions — it monitors after the fact and flags compliance violations for investigation. The rules it enforces are configured per merchant, per jurisdiction, per event type.

**SOX-relevant events:**
- Any modification to a price master record without an approved commercial workflow event in the preceding sequence (unauthorized price change signal)
- OTB commitment events that exceed the funded wallet balance at the time of commitment (the L402 gate should prevent this; if it appears in the event log anyway, it is an integrity violation)
- Receiving events without receiver attribution (anonymous receiving events are inadmissible for audit purposes)

**PII in event payloads:**
- The compliance agent scans incoming event payloads for PII patterns: unmasked card numbers, full SSNs, unmasked date-of-birth strings, full names in fields where only a badge number or user ID is required
- PII detected in a payload triggers a flagging event in the chain (the original event is not modified — the chain is immutable) and a remediation workflow for the receiving operative and their manager
- Configured PII fields (customer email in loyalty events, for example) are masked at write time by the platform, not by the compliance agent — the compliance agent catches any that slip through

**GDPR right-to-erasure handling:**
- The hash chain cannot be erased without breaking chain integrity
- The platform implements tombstoning: on receipt of a verified right-to-erasure request for a subject's data, the platform re-writes the PII fields in the original event payload as null values, re-hashes the tombstoned payload, and writes a tombstone event to the chain documenting the erasure request, the original event hash, and the tombstoned event hash
- The original event hash is now invalid; the tombstone event chain is the valid sequence
- This approach satisfies GDPR erasure requirements while maintaining chain integrity: the event record exists, the sequence is unbroken, the PII is gone

**HIPAA-relevant events:**
- Transactions involving controlled substance OTC products, pharmacy-adjacent items, or age-restricted health products (where applicable) are classified as health-adjacent at the item authorization level
- The compliance agent flags any such transaction that is missing required verification fields (age verification outcome, ID check reference) before a set retention window closes
- This is relevant for Murdoch's (OTC pharmaceuticals, certain agricultural chemicals) and generalizes to any retailer with health-adjacent assortment

**GDPR vs. CCPA/US state privacy laws:**
- The compliance agent's PII rules are jurisdiction-configurable
- US retailers default to CCPA-equivalent PII handling plus HIPAA for health-adjacent items
- Retailers with international customers or cross-border data flows configure GDPR rules on top of the US base

## The SMB gap this fills

A small retailer in 2026 has no visibility into:
- What devices are on their store network
- Whether their router has default credentials
- Whether a vendor left a device behind
- Whether their POS is exhibiting skimmer-pattern behavior
- Whether their event log has integrity gaps
- Whether their event payloads contain PII they didn't intend to write

These are not exotic security concerns. They are the everyday operational security posture of a retailer who is managing 50 other things simultaneously. The VSM makes all of it observable — not as a separate security product the operator has to learn, but as signals that surface through the same Operations Agent dashboard they are already using to manage shrink and OTB.

For the enterprise retailer, these functions exist in separate tools: SIEM for network monitoring, DLP for PII, audit team for SOX, legal team for GDPR. The platform delivers them as a unified capability at a price point the SMB retailer can access.

## What does not exist yet

The device manifest, network monitoring, compliance agent, and VSM self-monitoring are architecture. They require:
- Network access from the VSM (either via a store-side agent with local network access, or via integration with the store's managed network device — the router or switch — via its management API)
- A device fingerprinting library (OS detection, port profile, traffic pattern classification)
- Compliance rule configuration per merchant
- The tombstoning workflow for GDPR erasure

The hash chain infrastructure and the event stream subscriber pattern already exist. The compliance monitoring rules are the first build target. Network device monitoring requires the store-side agent, which is a later-stage capability.

## Related

- [[platform-field-capture]] — the capture tool the VSM monitors for usage compliance
- [[platform-thesis]] — Rail 1 (no unknown loss) and Rail 3 (no unanchored record) that store integrity monitoring enforces
- [[raas-receipt-as-a-service]] — the chain the VSM monitors for sequence integrity
- [[retail-item-authorization]] — compliance monitoring for regulatory zone enforcement and age verification
- [[platform-performance-nfrs]] — the VSM's own latency and write rate SLAs
- [[icp-murdochs-reference]] — firearms, NICS, OTC pharma, live animals — the compliance complexity that makes this capability necessary
