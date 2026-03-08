# Solana Wallet Integration & Setup (SpeedRay)

This guide covers **backend Solana config**, **frontend wallet connection** (Phantom, Solflare, etc.), and how they work with the **Sign** button and "Verified on Solana" timestamp.

---

## 1. Backend setup (Solana RPC & server keypair)

The backend can submit log entries to Solana using a **server-side keypair** (no user wallet). Configure via env or `.env`:

| Variable | Description | Example |
|----------|-------------|--------|
| `SPEEDRAY_SOLANA_RPC_URL` | Solana RPC endpoint | `https://api.mainnet-beta.solana.com` or `https://api.devnet.solana.com` |
| `SPEEDRAY_SOLANA_PRIVATE_KEY` | Base58 private key for the server wallet (optional) | From Phantom: Settings → Export Private Key, or generate with `solana-keygen new` |
| `SPEEDRAY_SOLANA_LOG_PROGRAM_ID` | Your on-chain program ID for the log (optional) | e.g. your deployed program’s public key |

**Example `.env` (devnet):**

```bash
SPEEDRAY_SOLANA_RPC_URL=https://api.devnet.solana.com
SPEEDRAY_SOLANA_PRIVATE_KEY=your_base58_private_key_here
SPEEDRAY_SOLANA_LOG_PROGRAM_ID=YourProgram111111111111111111111111111
```

- If these are **not set**, the backend returns `"Solana not configured"` and no transaction is sent.
- The backend currently returns a **placeholder signature** until you implement the real program call in `backend/storage/solana_client.py`.

**Python deps (already in backend):** `solana-py`, `solders` (see `backend/requirements.txt`).

---

## 2. Frontend: Solana wallet (user connects Phantom, etc.)

Users connect their **browser wallet** (Phantom, Solflare, etc.) so the UI can show “Connected” and optionally sign transactions.

### 2.1 Install wallet adapter packages

From the **project root** (where `package.json` is):

```bash
npm install @solana/wallet-adapter-base @solana/wallet-adapter-react @solana/wallet-adapter-react-ui @solana/wallet-adapter-wallets @solana/web3.js
```

### 2.2 Install a wallet (for testing)

- **Phantom:** [phantom.app](https://phantom.app) → install the browser extension.
- **Solflare:** [solflare.com](https://solflare.com) → install the browser extension.

Create or import a wallet. For testing, use **Devnet**: in Phantom go to Settings → Developer Settings → Change Network → Devnet.

### 2.3 How the frontend uses the wallet

- The app is wrapped in **`WalletProvider`** (see `src/wallet/WalletProvider.tsx`).
- The **Demo** page shows a **“Connect wallet”** control and a **“Sign”** button. After the user clicks **Sign**, a popup confirms “ER department has received the result” and the UI shows **“Verified on Solana”** with the signed timestamp.
- Optionally, the **Sign** action can send the log payload to your **backend** (`POST /log/submit`); the backend can use its **server keypair** to submit to Solana. By default, signing only records the timestamp and shows “Verified on Solana” without a blockchain call.

---

## 3. Flow summary

| Step | Who | What |
|------|-----|------|
| 1 | User | Connects wallet (Phantom/Solflare) in the app. |
| 2 | User | Runs pipeline, gets report, clicks **Sign**. |
| 3 | Frontend | Calls `POST /api/log/submit` with `run_id`, `study_id`, `payload` (and optionally `wallet_public_key`). |
| 4 | Backend | Uses `SPEEDRAY_SOLANA_PRIVATE_KEY` + RPC to submit (or simulate) the log transaction. |
| 5 | Backend | Returns `{ success, signature, error }`; frontend shows the signature in the submission log. |

---

## 4. Optional: use Devnet first

1. Set `SPEEDRAY_SOLANA_RPC_URL=https://api.devnet.solana.com`.
2. In Phantom (or your wallet), switch to **Devnet**.
3. Get devnet SOL from a [Devnet faucet](https://faucet.solana.com/) for the server wallet address (if you submit real transactions).
4. Deploy your log program to **Devnet** and set `SPEEDRAY_SOLANA_LOG_PROGRAM_ID` to that program ID.

---

## 5. References

- [Solana Wallet Adapter](https://github.com/solana-labs/wallet-adapter)
- [Solana Web3.js](https://solana-labs.github.io/solana-web3.js/)
- [Phantom](https://phantom.app) | [Solflare](https://solflare.com)
- Backend log submission: `backend/storage/solana_client.py` and `backend/api/routes/log.py`
