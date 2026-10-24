> ## Documentation Index
> Fetch the complete documentation index at: https://docs.limitless.exchange/llms.txt
> Use this file to discover all available pages before exploring further.

# Smart Contracts

> On-chain contract addresses for Limitless Exchange on Base

## Overview

Limitless Exchange runs on **Base** (Ethereum L2). All trading is settled on-chain via smart contracts.

> [!WARNING]
>
> To pull Limitless trading metrics, query **all three venue versions** of smart contracts. Each processes active trades. Partial queries give you incomplete data.

## Key token addresses

| Token | Address | Standard |
| - | - | - |
| **USDC** (Native on Base) | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | ERC-20 |
| **Conditional Tokens (CTF)** | `0xC9c98965297Bc527861c898329Ee280632B76e18` | ERC-1155 |

## Conditional tokens

Limitless uses the [Gnosis Conditional Tokens Framework (CTF)](https://docs.gnosis.io/conditionaltokens/) — an ERC-1155 token standard that enables the creation of conditional outcome tokens for any future event. When a market is created, the CTF contract mints Yes and No tokens representing each outcome. These tokens are freely tradeable and composable with other DeFi protocols.

The CTF is the underlying primitive that powers all market mechanics on Limitless, including share merging/splitting, NegRisk conversions, and market resolution payouts.

## Simple markets

### v1

| Contract | Address |
| - | - |
| CTF Exchange | `0xa4409D988CA2218d956BeEFD3874100F444f0DC3` |
| Fee Module | `0x6d8A7D1898306CA129a74c296d14e55e20aaE87D` |

### v2

| Contract | Address |
| - | - |
| CTF Exchange | `0xF1De958F8641448A5ba78c01f434085385Af096D` |
| Fee Module | `0xEECD2Cf0FF29D712648fC328be4EE02FC7931c7A` |

### v3

| Contract | Address |
| - | - |
| CTF Exchange | `0x05c748E2f4DcDe0ec9Fa8DDc40DE6b867f923fa5` |
| Fee Module | `0x5130c2c398F930c4f43B15635410047cBEa9D6EB` |
| Fee Module ([new trading venues](https://docs.limitless.exchange/developers/migrate-to-new-trading-venues.md)) | `0x7B6ffe5bA8B5ec7afB0AaBaE629D12dA5bC62565` |

## NegRisk markets

### v1

| Contract | Address |
| - | - |
| NegRisk Adapter | `0xb8DAA4C8C9f690396f671BB601727A4c3741340C` |
| NegRisk CTF Exchange | `0x5a38afc17F7E97ad8d6C547ddb837E40B4aEDfC6` |
| NegRisk Fee Module | `0x73FC1B1395bA964FEa8705BfF7eF8EA5C23CC661` |
| NegRisk Operator | `0xAE363abc7B264755e8706D81475C3586D4543992` |
| NegRisk Vault | `0x80307da4d8EA92Cd7a13bBf6B3309431Ca7a1c0E` |
| Wrapped Collateral | `0x5d6c6a4fea600e0b1a3ab3ef711060310e27886a` |

### v2

| Contract | Address |
| - | - |
| NegRisk Adapter | `0x7afeB946986211950d17f24176039F12c2aB2436` |
| NegRisk CTF Exchange | `0x46e607D3f4a8494B0aB9b304d1463e2F4848891d` |
| NegRisk Fee Module | `0x18B3E1192c01286050A0994Bc26f7226Ae4A483d` |
| NegRisk Operator | `0xd2e4a23E57F67a90Bfc999d420fDA16De0Fb2751` |
| NegRisk Vault | `0xd7d245CB2cbE55633e270aF8379E5D4AbA87BD58` |
| Wrapped Collateral | `0x428F0FC93221A9957dC667baa07E62d50c6b8c03` |

### v3

| Contract | Address |
| - | - |
| NegRisk Adapter | `0x6151EF8368b6316c1aa3C68453EF083ad31E712D` |
| NegRisk CTF Exchange | `0xe3E00BA3a9888d1DE4834269f62ac008b4BB5C47` |
| NegRisk Fee Module | `0xfeb646D32a2A558359419a1C9c5dfb47fD92dADb` |
| NegRisk Fee Module ([new trading venues](https://docs.limitless.exchange/developers/migrate-to-new-trading-venues.md)) | `0x01b7dF643247B377D5c39FcC40b9c28B4A827524` |
| NegRisk Operator | `0xB7D463037836cFf84FA9ddC25c1136756B4b5F61` |
| NegRisk Vault | `0x2eC22ee9381D0b3570cCb5887960DDFd05d210b3` |
| Wrapped Collateral | `0xBd8Ff5Ac78A3739037FEaA18278cC157C4798B01` |


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.