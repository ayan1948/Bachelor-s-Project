# Keysight Control Thesis

## Overview
Automating High Voltage Discharges over spark gaps and data retrieval. This project includes a FastAPI backend for controlling hardware and a SvelteKit frontend for the dashboard. Designed to run on a Raspberry Pi 4 with Ubuntu 18.04.

## Tech Stack
### Backend
- **Language:** Python 3
- **Framework:** FastAPI
- **Real-time:** FastAPI-SocketIO
- **ORM:** SQLAlchemy
- **Database:** SQLite
- **Libraries:** PyVISA, pyUSB, NumPy, SciPy, Matplotlib

### Frontend
- **Framework:** SvelteKit (Svelte 4)
- **Build Tool:** Vite
- **Package Manager:** npm

## Requirements
### Hardware
- Keysight Oscilloscope
- Raspberry Pi 4
- Relay Actuator (5V and 7KV)

### Software
- Python 3.8+
- Node.js (v18+) & npm
- [NI-VISA](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html) or [Keysight IO Libraries](https://www.keysight.com/us/en/lib/resources/software-downloads/io-libraries-suite.html) (for Oscilloscope communication)

> **Note:** Keysight officially supports specific Linux distributions (e.g., Ubuntu 16.04/18.04, RHEL 7.x).

## Setup & Run

### Backend
1. Navigate to the `Application` directory:
   ```bash
   cd Application
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python main.py
   ```
   The API will be available at `http://127.0.0.1:5000`.

### Frontend
1. Navigate to the `WebAppFrontend` directory:
   ```bash
   cd WebAppFrontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The dashboard will be available at `http://localhost:5173`.

## Project Structure
- `Application/`: FastAPI backend source code.
  - `main.py`: Entry point for the backend.
  - `models.py`: Database models.
  - `scope_manager.py`: Logic for oscilloscope communication.
  - `mock.py`: Mock ScopeManager for testing without hardware.
- `WebAppFrontend/`: SvelteKit frontend source code.
  - `src/routes/`: Application pages (Login, Register, Dashboard, Review).
- `results/`: (Generated) Directory for storing test results.

## Scripts
- **Backend:** `python main.py`
- **Frontend:**
  - `npm run dev`: Start dev server.
  - `npm run build`: Build for production.
  - `npm run preview`: Preview production build.

## Environment Variables
- TODO: Add support for `.env` files for `SECRET_KEY` and other configurations.

## Tests
- TODO: Implement unit and integration tests.

## License
- TODO: Add license information.
