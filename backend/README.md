# Aetherstore Engine Backend

## Overview
The Aetherstore Engine backend is a comprehensive 3D fashion platform API built with FastAPI. It includes advanced 3D asset processing capabilities using the Immersive Web SDK (IWSDK) integration.

## Features

### Core Platform Features
- **3D Store Management**: Create and manage virtual 3D stores
- **Product Catalog**: Manage 3D fashion products with detailed metadata
- **User Management**: Secure user authentication and profile management
- **Shopping Cart**: Full e-commerce functionality with cart management
- **Order Processing**: Complete order processing and fulfillment
- **Analytics**: Comprehensive analytics and reporting

### 3D Asset Pipeline
- **Model Processing**: Advanced 3D model optimization and conversion
- **Texture Optimization**: Image compression and format conversion
- **Avatar System**: 3D avatar creation from measurements
- **Try-On System**: Virtual try-on with physics simulation
- **Asset Management**: Complete asset lifecycle management

### IWSDK Integration
- **Immersive Web Technologies**: WebXR support for VR/AR experiences
- **Advanced Rendering**: High-performance 3D rendering with optimizations
- **Interaction Systems**: Natural 3D interactions with hand tracking
- **Locomotion**: Smooth movement in 3D spaces
- **Physics Simulation**: Realistic cloth and object physics

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Users     │  │   Stores    │  │  Products   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Avatars    │  │   Try-On    │  │   Orders    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Analytics   │  │     AI      │  │     VR      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                   Business Logic Layer                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Database   │  │ 3D Assets   │  │    AI       │        │
│  │   Models    │  │ Processing  │  │ Processing  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Storage    │  │ Analytics   │  │   Cache     │        │
│  │   System    │  │   Engine    │  │   System    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │   Files     │  │   Redis     │        │
│  │   Database  │  │  Storage    │  │   Cache     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 3D Asset Pipeline Components

### Asset Management System
Manages the complete lifecycle of 3D assets from upload to delivery.

#### Features:
- Asset upload and validation
- Metadata extraction
- Processing queue management
- Storage optimization
- Version control
- Access control

### 3D Model Processor
Processes and optimizes 3D models for web delivery.

#### Features:
- Format conversion (GLB, GLTF, OBJ, FBX, etc.)
- Polygon reduction and mesh optimization
- Texture compression (KTX2, WebP, DDS)
- LOD (Level of Detail) generation
- Physics property calculation
- Animation optimization

### Texture Optimizer
Optimizes textures for web delivery while maintaining quality.

#### Features:
- Format conversion (JPEG, PNG, WebP, KTX2)
- Resolution scaling
- Compression optimization
- Mipmap generation
- Color space management

### Avatar System
Creates and manages personalized 3D avatars from user measurements.

#### Features:
- Measurement-based avatar generation
- Body type classification
- Customization options
- Clothing integration
- Animation support

### Try-On Engine
Enables virtual try-on experiences with physics simulation.

#### Features:
- Cloth simulation
- Fit analysis
- Size recommendations
- Pose management
- Real-time rendering

## IWSDK Integration

### Core Systems
- **XR Input Management**: Advanced input handling with hand tracking
- **Locomotion System**: Smooth movement with comfort features
- **Grab System**: Natural object interaction
- **Spatial Audio**: 3D positional audio
- **Scene Understanding**: Environment detection and mapping

### Performance Optimizations
- **Draw Call Reduction**: 70% fewer draw calls through optimized input management
- **Persistent Input Spaces**: Maintain object attachments even when devices disconnect
- **Worker-Based Simulation**: Offload physics to background threads
- **Adaptive Quality**: Dynamic adjustment based on device performance

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Token refresh

### Users
- `GET /api/users/me` - Get current user
- `PUT /api/users/me` - Update current user
- `DELETE /api/users/me` - Delete current user

### Stores
- `POST /api/stores` - Create store
- `GET /api/stores` - List stores
- `GET /api/stores/{id}` - Get store
- `PUT /api/stores/{id}` - Update store
- `DELETE /api/stores/{id}` - Delete store

### Products
- `POST /api/products` - Create product
- `GET /api/products` - List products
- `GET /api/products/{id}` - Get product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### Avatars
- `POST /api/avatars` - Create avatar
- `GET /api/avatars/me` - Get current user's avatar
- `PUT /api/avatars/me` - Update current user's avatar
- `DELETE /api/avatars/me` - Delete current user's avatar

### Try-On
- `POST /api/tryon` - Create try-on session
- `GET /api/tryon` - List try-on sessions
- `GET /api/tryon/{id}` - Get try-on session
- `PUT /api/tryon/{id}` - Update try-on session
- `DELETE /api/tryon/{id}` - Delete try-on session

### Orders
- `POST /api/orders` - Create order
- `GET /api/orders` - List orders
- `GET /api/orders/{id}` - Get order
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order

## Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Node.js 16+ (for frontend)
- Redis (for caching)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/aetherstore-engine.git
cd aetherstore-engine/backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-3d.txt
```

3. Set up environment variables:
```bash
cp .env.template .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
# Create database
createdb aetherstore_dev

# Run migrations
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn main:app --reload
```

### Running Tests
```bash
pytest
```

### Building for Production
```bash
# Build the application
python -m build

# Run with production settings
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 3D Asset Processing

### Supported Formats
- **3D Models**: GLB, GLTF, OBJ, FBX, PLY, STL
- **Textures**: JPEG, PNG, WebP, KTX2, DDS
- **Animations**: BVH, FBX
- **Scans**: PLY, OBJ, STL

### Processing Pipeline
1. **Upload**: Assets are uploaded via API
2. **Validation**: File format and integrity validation
3. **Analysis**: Metadata extraction and quality assessment
4. **Optimization**: Format conversion and size reduction
5. **Storage**: Assets stored in optimized format
6. **Delivery**: Assets served via CDN

### Quality Levels
- **Low**: Fastest processing, largest files
- **Medium**: Balanced processing and size
- **High**: Slower processing, smaller files
- **Ultra**: Slowest processing, smallest files

## Performance Monitoring

### Metrics Tracked
- API response times
- Database query performance
- Asset processing times
- User engagement metrics
- System resource usage

### Optimization Strategies
- Caching with Redis
- Database indexing
- Asset compression
- CDN distribution
- Load balancing

## Security

### Authentication
- JWT tokens for API authentication
- OAuth2 password flow
- Session management

### Data Protection
- Password hashing with bcrypt
- Data encryption at rest
- HTTPS enforcement
- CORS protection

### Access Control
- Role-based permissions
- Resource ownership validation
- Rate limiting
- Input validation

## Extending the Platform

### Adding New Features
1. Create new API endpoints in `api/` directory
2. Add database models in `models.py`
3. Implement CRUD operations in `crud.py`
4. Add business logic in service files
5. Update API documentation

### Custom 3D Processing
1. Extend `3d_processing.py` with new processors
2. Add new asset types to `asset_pipeline.py`
3. Implement optimization algorithms
4. Add support for new file formats

### IWSDK Extensions
1. Add new IWSDK components
2. Implement additional WebXR features
3. Extend locomotion and interaction systems
4. Add support for new devices

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database URL in `.env`
   - Verify PostgreSQL is running
   - Ensure database user has proper permissions

2. **Asset Processing Failures**
   - Check file format support
   - Verify sufficient disk space
   - Check processing logs for details

3. **Performance Issues**
   - Monitor system resources
   - Check database query performance
   - Optimize asset processing settings

4. **IWSDK Integration Problems**
   - Verify browser WebXR support
   - Check WebGL compatibility
   - Ensure HTTPS for production deployment

### Logs and Debugging
- Check `logs/` directory for application logs
- Use `DEBUG=True` in `.env` for development
- Monitor database logs for query issues
- Check browser console for frontend errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Write docstrings for functions
- Add unit tests for new features

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support
For support, please open an issue on GitHub or contact the development team.