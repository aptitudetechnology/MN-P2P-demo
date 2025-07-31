# ModularNucleoid P2P Demo #

🌐 **Fortran + WebAssembly + P2P = Decentralized Science Apps**

builds on : https://github.com/ccsb-scripps/ModularNucleoid
using : https://gws.phd/posts/fortran_wasm/
---

## What is ModularNucleoid?

ModularNucleoid is an experimental platform combining Fortran scientific computation, compiled to WebAssembly (WASM), and peer-to-peer (P2P) browser networking to create decentralized scientific applications—especially for nucleoid/DNA simulations.

---

## 🚀 Features & What You Can Do

- Compile your ModularNucleoid core Fortran logic to WebAssembly.
- Run heavy computations locally inside the browser using WASM.
- Distribute computation and data directly between peers using P2P technologies.
- Use WebRTC or libp2p to send/receive simulation data between browsers.
- Each peer executes simulations independently — no central server required.

---

## 🔁 P2P Architecture Overview

```
[User A] <--WebRTC/libp2p--> [User B] <---> [User C]
       |                           |               |
       |--- WASM Module (DNA calc) |               |
       |   Runs in-browser         |               |
```

Each browser instance:

- Loads the ModularNucleoid WebAssembly module.
- Accepts DNA sequences or parameters from other peers.
- Runs simulations or data transformations locally.
- Shares results and syncs data with other peers.

---

## 🔧 How to Implement It

### 1. Compile Fortran to WebAssembly

- Use `gfortran` → `emcc` or other toolchains to compile Fortran source code into WASM.

### 2. Create a JavaScript Wrapper

- Expose key WASM functions like `simulate_nucleoid(...)`.
- Manage WASM memory, buffers, and input/output conversion.

### 3. Use a P2P Library in JavaScript

Popular P2P libraries:

- 🔄 **libp2p** (robust, used in IPFS)
- 📡 **PeerJS** (easy WebRTC wrapper)
- 🔁 **Gun.js** (P2P data sync & storage)

Use these to:

- Exchange input parameters and output results.
- Coordinate distributed workloads between connected peers.

### 4. Optional: P2P Storage & Sync

- Use IPFS for sharing larger datasets or models.
- Use Gun.js or OrbitDB for mutable, decentralized shared state.

---

## 🔐 Bonus: Privacy & Security

- No central server means data stays on local peers unless explicitly shared.
- Ideal for sensitive scientific or medical data.
- Optionally encrypt data client-side (e.g. PGP in-browser) before P2P sharing.

---

## ⚡ Real-World Use Cases

- Browser-based nucleoid/DNA simulations distributed across a research network.
- Citizen science projects allowing collaborative DNA simulations.
- Offline-first scientific apps with peer sync when connectivity resumes.

---

## 📦 Included Demo

This project includes a minimal working prototype demonstrating:

- Loading a dummy WASM module simulating Fortran computation.
- Connecting two browser clients peer-to-peer via PeerJS.
- Sending a DNA sequence to a peer and receiving processed results.
- A Flask web interface with routes for dashboard, simulation, and P2P demo.

---

## 🚀 Getting Started

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the app:

```bash
python app.py
```

3. Open [http://localhost:5000](http://localhost:5000) in two different browsers or tabs to test P2P demo.

---

## 🛠️ Future Improvements

- Integrate real ModularNucleoid Fortran WASM modules.
- Expand P2P syncing logic and error handling.
- Add user authentication and data encryption.
- Enhance UI/UX for simulation parameter input and result visualization.

---

## 🤝 Contributing

Contributions and feedback are welcome! Please open issues or pull requests on GitHub.

---

## License

This project is licensed under the MIT License.

---

**ModularNucleoid P2P Demo** — Decentralized science in your browser.
