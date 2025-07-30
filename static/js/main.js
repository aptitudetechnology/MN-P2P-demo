let peer = new Peer(); // Generate random ID
let conn = null;

peer.on('open', id => {
  console.log("My peer ID is: " + id);
  alert("Your Peer ID: " + id);
});

peer.on('connection', c => {
  conn = c;
  conn.on('data', async data => {
    const result = await runWasm(data);
    conn.send(result);
  });
});

async function connect() {
  const destId = document.getElementById("peer-id").value;
  conn = peer.connect(destId);
  conn.on('data', data => {
    document.getElementById("result").textContent = "Peer says: " + data;
  });
}

function send() {
  const sequence = document.getElementById("sequence").value;
  if (conn && conn.open) {
    conn.send(sequence);
  }
}

// Dummy Wasm loader + GC content calculator
async function runWasm(dnaSeq) {
  const wasm = await WebAssembly.instantiateStreaming(fetch('calc.wasm'));
  const { gc_content } = wasm.instance.exports;

  const encoded = new TextEncoder().encode(dnaSeq);
  const mem = new Uint8Array(wasm.instance.exports.memory.buffer, 0, encoded.length);
  mem.set(encoded);

  const gc = gc_content(0, encoded.length); // Assume it reads memory directly
  return `GC content: ${gc}%`;
}
