# Maintaining

Document authority and currentness: [Documentation Index](README.md).

## Source Layout

```text
hv2                         stable source/installed launcher
PRODUCT-CAPABILITIES.json   dated claim boundary
src/hv2ref/cli.py           command and exit-code projection
src/hv2ref/carrier.py       protected Generation 1 release carrier
src/hv2ref/jsonio.py        canonical JSON and durability primitives
src/hv2ref/errors.py        stable contract error type
src/hv2ref/product.py       product release and binding lifecycle
src/hv2ref/state.py         protected Generation 1 state contract
src/hv2ref/parallel.py      protected Generation 2 contract
src/hv2ref/intent.py        protected Guided Intent contract
docs/                       canonical repository documentation
tests/                      stdlib contract and acceptance fixtures
receipts/                   retained historical evidence; not current by presence
```

## Validation

Run the full suite without repository bytecode artifacts:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -O -m unittest discover -s tests -v
git diff --check
```

`PYTHONDONTWRITEBYTECODE=1` is required because some regression fixtures start child Python processes that do not inherit the
parent interpreter’s `-B` flag. After validation, `find src -name __pycache__ -o -name '*.pyc'` must print nothing.

Productization changes also require fresh disposable Git targets for init/status/doctor/update/rollback/detach, interruption recovery,
managed drift, symlink/root escape, secret-sentinel invariance, manual detach audit, and repository-only reader verification.

## Lightweight Budget

The measurement tool is maintainer-only and is not a product runtime dependency. In an isolated environment with
`tiktoken==0.13.0` installed, use encoding `o200k_base` and these exact file sets:

- always loaded: `AGENTS.md`, limit `2,000` tokens;
- bootstrap: `AGENTS.md + README.md + docs/GETTING-STARTED.md`, limit `4,000` tokens and three mandatory reads.

Run from the contribution source root:

```sh
python3 -c 'from pathlib import Path; import tiktoken; e=tiktoken.get_encoding("o200k_base"); groups={"always_loaded":["AGENTS.md"],"bootstrap":["AGENTS.md","README.md","docs/GETTING-STARTED.md"]}; [print(k,len(e.encode("\n".join(Path(p).read_text(encoding="utf-8") for p in ps)))) for k,ps in groups.items()]'
```

Record the tiktoken version, encoding, file set, counts, and date together. A numeric pass does not replace the repository-only
reader fixture.

## Release Inventory

`src/hv2ref/product.py` owns the fixed `MANAGED_PATHS` set. A source-derived release inventories every path by UTF-8 relative name,
byte length, and SHA-256. Canonical inventory bytes derive the release ID. Extra, missing, symlinked, reordered, or digest-mismatched
release files fail verification.

Adding a managed path is a delivery-contract change. Update the path set, documentation index, productization tests, lightweight
budget, and detach coverage together. Do not add project-owned state, local configuration, secrets, tests, or retained receipts to
the managed release.

## Protected Surfaces

The D1 product layer is additive. `carrier.py`, `state.py`, `parallel.py`, `intent.py`, existing generation contracts, and retained
receipts remain protected during the current product lifecycle work. A blocking integration defect needs a separately reviewed
minimal delta and full regression scope.

The root launcher is byte-stable across D1 updates. Changing it requires an explicit migration gate because a failed launcher update
could remove the only project-local entry.

## Documentation Currentness

`docs/README.md` owns document type, authority, applicable surface, and verification state. Commands and docs change in the same
product revision. External learning or blog content links to a versioned canonical repository; it never owns current command or
support truth.

Public name, repository, license, SemVer, CI, package carrier, anonymous install, and runtime support promotion are separate D3 work.
Do not infer them from a green private test suite.
