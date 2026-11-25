# Legacy handoff inbox observation race

Status: Owner approved registration on 2026-11-25. Support decision pending.

In the earlier-generation handoff receiver, an inbox directory listing can contain a transient SQLite journal that has disappeared by the time its metadata is read. The observed failure occurs in `_delivery_db` when it inspects `inbox.db-journal`. A synthetic fixture reproduced `FileNotFoundError` during the observation. The installed ordinary and grouped Work paths checked in [Phase C](PATCH-20261125-002-read-path-efficiency-phase-c.md) did not reach the legacy inbox.

Determine which supported hosts or formats still use this receiver before designing a fix. If selected, reproduce the race on the supported entry and verify that expected journal churn cannot hide a missing durable user record or weaken directory identity checks. Keep the failed observation and any message delivery state available for recovery.
