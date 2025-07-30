# GitHub Copilot Instructions: ModularNucleoid P2P Demo

## Project Overview
This is a ModularNucleoid P2P Demo project that combines:
- **Fortran scientific computation** compiled to WebAssembly (WASM)
- **Peer-to-peer (P2P) browser networking** using WebRTC/PeerJS
- **Flask web application** with modular architecture
- **Decentralized DNA/nucleoid simulations** running in browsers

## Project Architecture

### Backend (Flask)
```
├── app.py                 # Main Flask application entry point
├── settings.py           # Configuration settings
├── paths.py              # Path configurations
├── routes/               # Modular route handlers
│   ├── main.py          # Main web routes
│   └── api.py           # API endpoints
├── utils/                # Utility modules
│   ├── database.py      # Database operations
│   ├── helpers.py       # Helper functions
│   └── validators.py    # Input validation
└── data/
    └── database.db      # SQLite database
```

### Frontend
```
├── templates/            # Jinja2 HTML templates
│   ├── base.html        # Base template
│   ├── dashboard.html   # Main dashboard
│   ├── p2p_demo.html    # P2P demonstration
│   ├── simulate.html    # Simulation interface
│   └── settings.html    # Settings page
└── static/
    ├── css/
    │   └── custom.css   # Custom styles
    └── js/
        ├── app.js       # Main application logic
        └── main.js      # P2P and WASM integration
```

## Core Components to Implement

### 1. P2P Networking with PeerJS
- Use PeerJS library for WebRTC connections
- Auto-generate peer IDs for each browser session
- Handle peer discovery and connection management
- Implement data exchange between connected peers
- Handle connection errors and reconnection logic

### 2. WebAssembly Integration
- Load Fortran-compiled WASM modules in browser
- Create JavaScript wrappers for WASM functions
- Manage memory allocation for WASM operations
- Handle data type conversion between JS and WASM
- Expose scientific computation functions (e.g., GC content calculation)

### 3. Scientific Computation Pipeline
- Accept DNA sequences as input
- Process sequences through WASM-compiled Fortran functions
- Return computational results to requesting peers
- Support distributed workload coordination
- Handle large dataset processing

## Code Patterns and Conventions

### JavaScript (Frontend)
```javascript
// P2P Connection Pattern
let peer = new Peer(); // Auto-generate ID
let conn = null;

peer.on('open', id => {
  console.log("Peer ID:", id);
});

peer.on('connection', connection => {
  conn = connection;
  conn.on('data', async data => {
    const result = await runWasm(data);
    conn.send(result);
  });
});

// WASM Integration Pattern
async function runWasm(inputData) {
  const wasm = await WebAssembly.instantiateStreaming(fetch('module.wasm'));
  const { scientific_function } = wasm.instance.exports;
  
  // Handle memory and data conversion
  const encoded = new TextEncoder().encode(inputData);
  const mem = new Uint8Array(wasm.instance.exports.memory.buffer, 0, encoded.length);
  mem.set(encoded);
  
  const result = scientific_function(0, encoded.length);
  return result;
}
```

### Python (Backend)
```python
# Flask Route Pattern
from flask import Blueprint, render_template, request, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/p2p-demo')
def p2p_demo():
    return render_template('p2p_demo.html')

# API Endpoint Pattern
@api_bp.route('/api/simulation', methods=['POST'])
def create_simulation():
    data = request.get_json()
    # Validate input
    # Store in database
    # Return response
    return jsonify({'status': 'success'})
```

### Fortran to WASM
```fortran
! Fortran function for WASM compilation
subroutine gc_content(ptr, length, result) bind(c)
  use iso_c_binding
  implicit none
  integer(c_int), value :: ptr, length
  real(c_float), intent(out) :: result
  
  ! Implementation here
end subroutine
```

## Key Features to Implement

### P2P Demo Page (`p2p_demo.html`)
- Peer ID display and connection interface
- DNA sequence input textarea
- Send/receive functionality
- Real-time result display
- Connection status indicators

### Simulation Interface (`simulate.html`)
- Parameter input forms for scientific simulations
- Result visualization components
- Progress indicators for long-running computations
- Export/import functionality for simulation data

### Dashboard (`dashboard.html`)
- Overview of active connections
- Recent simulation results
- System status and performance metrics
- Quick access to main features

## Dependencies and Libraries

### Frontend
- **PeerJS**: WebRTC P2P networking (`https://unpkg.com/peerjs@1.4.7/dist/peerjs.min.js`)
- **WebAssembly**: Native browser support for WASM modules
- **Modern JavaScript**: ES6+ features, async/await patterns

### Backend
- **Flask**: Web framework
- **SQLite**: Database for storing simulation data
- **Python 3.12+**: Modern Python features

## Development Guidelines

### When writing code, prioritize:
1. **Modular architecture** - Keep components separate and reusable
2. **Error handling** - P2P connections can be unreliable
3. **Performance** - WASM operations should be optimized
4. **Security** - Validate all peer-to-peer data exchange
5. **User experience** - Clear feedback for connection status and results

### File organization:
- Keep P2P logic in `static/js/main.js`
- Use Flask blueprints for route organization
- Store WASM files in `static/` directory
- Use database for persistent storage of results
- Implement proper logging for debugging P2P issues

### Testing considerations:
- Test P2P functionality across different browsers
- Verify WASM module loading and execution
- Test with various DNA sequence inputs
- Handle network connectivity issues gracefully

## Current Implementation Status
The project has a working Flask structure with:
- ✅ Modular route system
- ✅ Database integration
- ✅ Template system
- ✅ Static asset organization
- 🔄 P2P networking implementation (in progress)
- 🔄 WASM integration (in progress)
- 🔄 Scientific computation modules (planned)

## Next Steps for Development
1. Implement basic P2P connection in `main.js`
2. Create simple WASM module for testing
3. Build out P2P demo interface
4. Add database models for simulation storage
5. Implement real Fortran scientific functions
6. Add error handling and connection management
7. Create comprehensive testing suite

## Notes for AI Assistant
- This is a scientific computing project focused on decentralized simulations
- Privacy and security are important due to sensitive scientific data
- Performance optimization is crucial for scientific computations
- The project combines multiple technologies (Fortran, WASM, P2P, Flask)
- Code should be production-ready with proper error handling
- Follow modern web development best practices
- Consider scalability for multiple connected peers