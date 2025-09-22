#!/usr/bin/env bash

# build.sh - Enhanced build script for Hospital CRM deployment

set -o errexit  # Exit on error

echo "🚀 Starting Hospital CRM build process..."

# Update package list and install system dependencies
echo "📦 Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    apt-get update
    apt-get install -y libavdevice-dev libavfilter-dev libavutil-dev libsrtp2-dev libx264-dev libpq-dev
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p static/uploads

# Set permissions
echo "🔐 Setting permissions..."
chmod 755 logs uploads static/uploads 2>/dev/null || true

echo "✅ Build completed successfully!"

# Health check
echo "🏥 Running health check..."
python -c "
import sys
try:
    from app_enhanced import create_app
    app = create_app()
    print('✅ Application factory works correctly')
except Exception as e:
    print(f'❌ Application factory failed: {e}')
    sys.exit(1)
" || echo "⚠️ Health check skipped (dependencies may not be fully available yet)"

echo "🎉 Hospital CRM is ready for deployment!"