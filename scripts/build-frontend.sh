#!/bin/bash

# Build Frontend for Django Static Files
# This script builds the Vue.js frontend and moves it to Django's static directory

set -e  # Exit on any error

echo "🚀 Building Vue.js Frontend for Django..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_DIR/frontend"
STATIC_DIR="$PROJECT_DIR/static"
ADMIN_STATIC_DIR="$STATIC_DIR/admin"

echo -e "${BLUE}Project Directory: $PROJECT_DIR${NC}"
echo -e "${BLUE}Frontend Directory: $FRONTEND_DIR${NC}"
echo -e "${BLUE}Static Directory: $ADMIN_STATIC_DIR${NC}"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Frontend directory not found at $FRONTEND_DIR${NC}"
    exit 1
fi

# Navigate to frontend directory
cd "$FRONTEND_DIR"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ package.json not found in frontend directory${NC}"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi

# Create static directory if it doesn't exist
mkdir -p "$ADMIN_STATIC_DIR"

# Clean previous build
echo -e "${YELLOW}🧹 Cleaning previous build...${NC}"
rm -rf "$ADMIN_STATIC_DIR"/*

# Build the project
echo -e "${YELLOW}🏗️  Building Vue.js project...${NC}"
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build completed successfully!${NC}"
    echo -e "${GREEN}📁 Files built to: $ADMIN_STATIC_DIR${NC}"
    
    # List built files
    echo -e "${BLUE}📋 Built files:${NC}"
    find "$ADMIN_STATIC_DIR" -type f | sort
    
    # Get file count and size
    FILE_COUNT=$(find "$ADMIN_STATIC_DIR" -type f | wc -l)
    TOTAL_SIZE=$(du -sh "$ADMIN_STATIC_DIR" | cut -f1)
    
    echo -e "${GREEN}📊 Build Summary:${NC}"
    echo -e "   Files: $FILE_COUNT"
    echo -e "   Total Size: $TOTAL_SIZE"
    
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

# Optional: Create a build info file
BUILD_INFO_FILE="$ADMIN_STATIC_DIR/build-info.json"
cat > "$BUILD_INFO_FILE" << EOF
{
  "buildDate": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "buildUser": "$(whoami)",
  "buildHost": "$(hostname)",
  "gitCommit": "$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')",
  "gitBranch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')",
  "nodeVersion": "$(node --version)",
  "npmVersion": "$(npm --version)"
}
EOF

echo -e "${GREEN}✅ Build info saved to: $BUILD_INFO_FILE${NC}"

# Optional: Run Django collectstatic if manage.py exists
MANAGE_PY="$PROJECT_DIR/manage.py"
if [ -f "$MANAGE_PY" ]; then
    echo -e "${YELLOW}🐍 Running Django collectstatic...${NC}"
    cd "$PROJECT_DIR"
    python manage.py collectstatic --noinput --clear
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Django static files collected${NC}"
    else
        echo -e "${YELLOW}⚠️  Django collectstatic failed (this is okay if settings aren't configured)${NC}"
    fi
else
    echo -e "${YELLOW}ℹ️  manage.py not found, skipping Django collectstatic${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Frontend build completed successfully!${NC}"
echo -e "${BLUE}📝 Next steps:${NC}"
echo -e "   1. Start your Django server: python manage.py runserver"
echo -e "   2. Visit http://localhost:8000/admin/ to see the Vue.js admin"
echo -e "   3. The Django admin is still available at http://localhost:8000/django-admin/"
echo ""
echo -e "${YELLOW}💡 Pro tip: Run this script whenever you make changes to the frontend${NC}"
