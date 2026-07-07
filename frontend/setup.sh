#!/bin/bash
# PreStocks Frontend Setup Script
# Run this after installing Node.js (v18+ required)

set -e

echo "=== PreStocks Frontend Setup ==="
echo ""

# Check Node.js
if ! command -v node &>/dev/null; then
  echo "ERROR: Node.js is not installed."
  echo "Install Node.js v18+ from https://nodejs.org or use nvm:"
  echo "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash"
  echo "  nvm install 20"
  exit 1
fi

NODE_VERSION=$(node -v | cut -d'.' -f1 | tr -d 'v')
if [ "$NODE_VERSION" -lt 18 ]; then
  echo "ERROR: Node.js v18+ required. Current: $(node -v)"
  exit 1
fi

echo "✓ Node.js $(node -v)"
echo ""

# Install dependencies
echo "Installing dependencies..."
npm install

# Copy env file
if [ ! -f .env.local ]; then
  cp .env.local.example .env.local
  echo "✓ Created .env.local from example"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Start development server:"
echo "  npm run dev"
echo ""
echo "Open http://localhost:3000"
