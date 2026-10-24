> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# Security

> Smart contract architecture and security audits for Limitless Core

## Overview

Limitless Core is the on-chain primitive layer that powers the exchange. It runs on Base and is built on three contract suites, with no protocol-level custody of user funds.

## Limitless Core contracts

Three contract suites compose the core protocol. Full addresses for every deployed version are listed on the [Smart Contracts](https://docs.limitless.exchange/user-guide/smart-contracts.md) page.

### Gnosis Conditional Tokens Framework (CTF)

The ERC-1155 token primitive that represents Yes and No outcome shares for every market. Limitless uses the canonical Gnosis Conditional Tokens contract deployed on Base. It is the underlying settlement layer for share minting, merging, splitting, and redemption.

Reference: [Gnosis CTF documentation](https://docs.gnosis.io/conditionaltokens/)

### CTF Exchange (CLOB)

The central limit order book for trading Yes and No shares. Orders are signed off-chain with EIP-712 and matched on-chain against the CTF, with fees routed through a separate fee module. The CLOB is deployed in three concurrent versions (v1, v2, v3) to support active trading and gradual migration.

### NegRisk

The contract suite that powers mutually exclusive multi-outcome markets, for example "who wins the election". It includes an adapter, exchange, fee module, vault, and operator. Traders can convert a complete set of No shares across outcomes back into collateral. NegRisk is also deployed in three concurrent versions.

## Security audits

The smart contracts that power Limitless Core are forked from independently audited Polymarket contracts.

> **[CTF Exchange (CLOB)](https://github.com/Polymarket/ctf-exchange/blob/main/audit/ChainSecurity_Polymarket_Exchange_audit.pdf)**
>
> ChainSecurity audit of the upstream Polymarket CTF Exchange.

> **[NegRisk](https://github.com/Polymarket/neg-risk-ctf-adapter/blob/main/audit/Polymarket%20Multi-Outcome%20Markets%20Audit.pdf)**
>
> Audit of the upstream Polymarket multi-outcome markets adapter.

### Limitless modifications

Limitless maintains a public fork of the CTF Exchange at [limitless-labs-group/limitless-ctf-exchange](https://github.com/limitless-labs-group/limitless-ctf-exchange). Changes against the upstream audited codebase include:

* Added `LIMITLESS_SAFE` signature type for Limitless Safe smart-wallet orders (EIP-1271 compatible), replacing the upstream `POLY_GNOSIS_SAFE` type.
* Base-specific deployment configuration and domain separator.

These changes are not covered by the upstream ChainSecurity audit.

> [!NOTE]
>
> The Gnosis CTF is the canonical Conditional Tokens contract; refer to the upstream Gnosis audits for that codebase.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.