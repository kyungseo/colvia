# Fixed root-cache verifier fixture

Public signed metadata generated from an existing isolated test trust anchor. No private key is included or generated here. Version 2 retains the same trusted key roles and advances only the root version. Timestamp/snapshot/targets are the fixed version-1 metadata. Tests use reference time 2026-11-09 UTC within the signed validity interval; never use this fixture as a release trust source. The target archive is not included because these tests verify saved metadata without fetching payloads.
