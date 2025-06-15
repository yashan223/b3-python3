#!/bin/bash
# filepath: setup_b3.sh

echo "================================================"
echo "BigBrotherBot (B3) - Complete Setup Script"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons."
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-full \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    build-essential \
    git \
    curl \
    wget

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install core Python dependencies
print_status "Installing core Python dependencies..."
pip install \
    psycopg2-binary \
    mysql-connector-python \
    paramiko \
    lxml \
    pillow \
    requests \
    beautifulsoup4 \
    configparser \
    six \
    pytz

# Install additional dependencies that B3 might need
print_status "Installing additional dependencies..."
pip install \
    python-dateutil \
    setuptools \
    wheel \
    packaging

# Install optional dependencies for enhanced functionality
print_status "Installing optional dependencies..."
pip install \
    pycrypto \
    geoip2 \
    maxminddb \
    feedparser \
    python-memcached

# Create requirements.txt for future reference
print_status "Creating requirements.txt..."
pip freeze > requirements.txt

# Check if B3 files exist
if [ ! -f "b3_run.py" ]; then
    print_warning "b3_run.py not found. Make sure you have B3 files in this directory."
fi

# Create a simple activation script
print_status "Creating activation script..."
cat > activate_b3.sh << 'EOF'
#!/bin/bash
echo "Activating B3 virtual environment..."
source venv/bin/activate
echo "Virtual environment activated. You can now run B3 with:"
echo "python b3_run.py"
EOF

chmod +x activate_b3.sh

# Create a startup script for B3
print_status "Creating B3 startup script..."
cat > start_b3.sh << 'EOF'
#!/bin/bash
echo "Starting BigBrotherBot (B3)..."
source venv/bin/activate
python b3_run.py "$@"
EOF

chmod +x start_b3.sh

# Create a simple systemd service file (optional)
print_status "Creating systemd service template..."
cat > b3.service.template << EOF
[Unit]
Description=BigBrotherBot (B3)
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python $(pwd)/b3_run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_status "Setup completed successfully!"
echo ""
echo "================================================"
echo "Setup Summary:"
echo "================================================"
echo "✓ System dependencies installed"
echo "✓ Python virtual environment created"
echo "✓ Python packages installed"
echo "✓ Helper scripts created"
echo ""
echo "To use B3:"
echo "1. Activate the environment: source venv/bin/activate"
echo "2. Or use the helper script: ./activate_b3.sh"
echo "3. Or start B3 directly: ./start_b3.sh"
echo ""
echo "To install as a system service:"
echo "1. Copy b3.service.template to /etc/systemd/system/b3.service"
echo "2. Edit the service file as needed"
echo "3. Run: sudo systemctl enable b3 && sudo systemctl start b3"
echo ""
echo "Virtual environment location: $(pwd)/venv"
echo "Requirements saved to: requirements.txt"
echo "================================================"
