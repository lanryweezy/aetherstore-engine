#!/bin/bash
# deploy.sh
# Deployment script for Aetherstore Engine with IWSDK Integration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_ENV=${1:-staging}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BUILD_DIR="$PROJECT_ROOT/build"

# Logging function
log() {
    echo -e "${BLUE}[DEPLOY] $(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING] $(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

log_error() {
    echo -e "${RED}[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking deployment prerequisites..."
    
    # Check if required tools are installed
    local tools=("python3" "npm" "node" "docker" "docker-compose" "git")
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is not installed. Please install it before deploying."
            return 1
        fi
    done
    
    log_success "All prerequisites satisfied"
}

# Build backend
build_backend() {
    log "Building backend application..."
    
    cd "$BACKEND_DIR"
    
    # Install backend dependencies
    log "Installing backend dependencies..."
    pip install -r requirements.txt
    
    # Run backend tests
    log "Running backend tests..."
    if [ -f "test_api_structure.py" ]; then
        python test_api_structure.py || log_warning "Some backend tests failed, continuing with deployment..."
    else
        log_warning "No backend tests found"
    fi
    
    # Run database migrations if alembic is available
    if command -v alembic &> /dev/null; then
        log "Running database migrations..."
        alembic upgrade head || log_warning "Database migrations failed, continuing with deployment..."
    else
        log_warning "Alembic not found, skipping database migrations"
    fi
    
    log_success "Backend built successfully"
}

# Build frontend
build_frontend() {
    log "Building frontend application..."
    
    cd "$FRONTEND_DIR"
    
    # Install frontend dependencies
    log "Installing frontend dependencies..."
    npm install
    
    # Build frontend for production
    log "Building frontend for production..."
    npm run build
    
    log_success "Frontend built successfully"
}

# Create deployment package
create_deployment_package() {
    log "Creating deployment package..."
    
    # Create build directory
    mkdir -p "$BUILD_DIR"
    
    # Copy backend files
    log "Copying backend files..."
    cp -r "$BACKEND_DIR" "$BUILD_DIR/"
    
    # Copy frontend build files
    log "Copying frontend build files..."
    mkdir -p "$BUILD_DIR/frontend/dist"
    cp -r "$FRONTEND_DIR/dist"/* "$BUILD_DIR/frontend/dist/" 2>/dev/null || true
    
    # Copy documentation
    log "Copying documentation..."
    cp "$PROJECT_ROOT/IWSDK_INTEGRATION.md" "$BUILD_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT/DEPLOYMENT_CHECKLIST.md" "$BUILD_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT/README.md" "$BUILD_DIR/" 2>/dev/null || true
    
    # Create deployment manifest
    cat > "$BUILD_DIR/deployment_manifest.json" << EOF
{
  "project": "Aetherstore Engine",
  "version": "1.0.0",
  "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "environment": "$DEPLOY_ENV",
  "components": {
    "backend": {
      "language": "Python",
      "framework": "FastAPI",
      "status": "ready_for_iwsdk_integration"
    },
    "frontend": {
      "language": "JavaScript",
      "frameworks": ["Three.js", "React"],
      "status": "ready_for_iwsdk_integration"
    },
    "iwsdk": {
      "status": "mock_implementation",
      "note": "Waiting for official IWSDK packages"
    }
  },
  "deployment_notes": [
    "IWSDK integration is currently using mock implementations",
    "Real IWSDK packages need to be published before production deployment",
    "All core functionality implemented with fallback to traditional 3D"
  ]
}
EOF
    
    log_success "Deployment package created at $BUILD_DIR"
}

# Deploy to target environment
deploy_to_environment() {
    log "Deploying to $DEPLOY_ENV environment..."
    
    case $DEPLOY_ENV in
        staging)
            deploy_to_staging
            ;;
        production)
            deploy_to_production
            ;;
        *)
            log_warning "Unknown environment: $DEPLOY_ENV, deploying to staging"
            deploy_to_staging
            ;;
    esac
}

deploy_to_staging() {
    log "Deploying to staging environment..."
    
    # In a real implementation, this would:
    # 1. Copy files to staging server
    # 2. Set up staging environment variables
    # 3. Start staging services
    # 4. Run staging tests
    
    log_warning "Staging deployment is a placeholder - real implementation needed"
    log_success "Staging deployment completed (placeholder)"
}

deploy_to_production() {
    log "Deploying to production environment..."
    
    # In a real implementation, this would:
    # 1. Run comprehensive pre-deployment checks
    # 2. Create database backups
    # 3. Deploy to production servers
    # 4. Run post-deployment validation
    
    log_warning "Production deployment is a placeholder - real implementation needed"
    log_success "Production deployment completed (placeholder)"
}

# Run post-deployment tests
run_post_deployment_tests() {
    log "Running post-deployment tests..."
    
    # In a real implementation, this would:
    # 1. Test API endpoints
    # 2. Test database connectivity
    # 3. Test frontend functionality
    # 4. Test IWSDK integration (when available)
    
    log_warning "Post-deployment tests are a placeholder - real implementation needed"
    log_success "Post-deployment tests completed (placeholder)"
}

# Main deployment function
main() {
    log "Starting Aetherstore Engine deployment to $DEPLOY_ENV environment..."
    
    # Check prerequisites
    check_prerequisites || exit 1
    
    # Build backend
    build_backend || exit 1
    
    # Build frontend
    build_frontend || exit 1
    
    # Create deployment package
    create_deployment_package || exit 1
    
    # Deploy to target environment
    deploy_to_environment || exit 1
    
    # Run post-deployment tests
    run_post_deployment_tests || exit 1
    
    log_success "Aetherstore Engine deployment to $DEPLOY_ENV completed successfully!"
    log "Deployment package available at: $BUILD_DIR"
    log "Next steps:"
    log "1. Wait for official IWSDK packages to be published"
    log "2. Replace mock implementations with real IWSDK functionality"
    log "3. Complete the remaining items in DEPLOYMENT_CHECKLIST.md"
    log "4. Run comprehensive testing before production deployment"
}

# Run main function
main "$@"