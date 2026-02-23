# IWSDK Integration for Aetherstore Engine

## Overview

This project demonstrates the integration of the Immersive Web SDK (IWSDK) into the Aetherstore Engine, a 3D fashion e-commerce platform. The IWSDK integration enhances the immersive shopping experience with advanced XR capabilities.

## IWSDK Features Implemented

### 1. Modern Architecture
- ECS (Entity Component System) implementation for scalable 3D objects
- Performance optimizations with reduced draw calls through IWSDK's input management
- Persistent input spaces that maintain object attachments even when devices disconnect

### 2. Input Management System
- Customizable input management separating input visualization, spaces, and gamepad utilities
- Reliable controller input handling with improved performance
- Pointer-events for natural web-like interactions

### 3. Interaction Systems
- Ray-based and proximity-based interactions
- W3C-compliant pointer events for familiar development patterns
- Hand tracking and gesture recognition support

### 4. Locomotion System
- Multiple movement modes: slide locomotion with vignetting, teleportation, and turn options
- Performance optimization with worker-based simulation
- User comfort features with configurable vignetting intensity

### 5. Grab Interactions
- Six different grabbable components for complex interaction behaviors
- Support for one or two-handed grabs and distance grab functionality

### 6. Spatial Audio
- Automatic 3D positioning, distance attenuation, and audio lifecycle management
- Easy integration through audio component attachment

## IWSDK Simulation Layer

Since the real IWSDK packages are not yet available, this implementation includes a comprehensive simulation layer that mimics the actual IWSDK functionality:

- `iw-sdk-core.js` - Core IWSDK system with all subsystems
- `iw-sdk-integration.js` - Integration layer with Aetherstore Engine
- `iw-sdk-store.js` - IWSDK-enhanced 3D store scene
- `iw-sdk-product-display.js` - Product display system
- `iw-sdk-avatar.js` - Avatar system
- `iw-sdk-try-on.js` - Try-on functionality
- `iw-sdk-commerce-analytics.js` - Analytics integration

## Security Implementation

The integration includes comprehensive security measures:

- Authentication and authorization
- Input validation and sanitization
- CSRF protection
- XSS prevention
- Secure API request handling

## Error Handling

Robust error handling throughout the application:

- Global error monitoring
- API request error handling
- 3D asset loading error handling
- IWSDK system error handling
- Graceful fallbacks

## Performance Optimizations

- Code splitting and lazy loading
- Asset optimization and compression
- Efficient rendering techniques
- Memory management
- Webpack optimization for production builds

## Development

### Installation
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

### Running the Build Script
```
build_production.bat
```

## Architecture

```
┌─────────────────────────────────────────┐
│            Aetherstore Engine           │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐    │
│  │      IWSDK Integration        │    │
│  │  ┌─────────────────────────┐   │    │
│  │  │   IWSDK Core System   │   │    │
│  │  ├─────────────────────────┤   │    │
│  │  │ • Input Management    │   │    │
│  │  │ • Locomotion System   │   │    │
│  │  │ • Grab System         │   │    │
│  │  │ • Spatial Audio       │   │    │
│  │  └─────────────────────────┘   │    │
│  └─────────────────────────────────┘    │
├─────────────────────────────────────────┤
│        Security & Error Handling        │
├─────────────────────────────────────────┤
│         Production Optimizations        │
└─────────────────────────────────────────┘
```

## IWSDK APIs Used

### Core IWSDK Systems
```javascript
// IWSDK Core
IWSDK.instance.initialize(config);

// Input Management
const xrInput = IWSDK.instance.getSystem('xrInput');
xrInput.on('controllerconnected', callback);

// Locomotion System
const locomotion = IWSDK.instance.getSystem('locomotion');
locomotion.initialize(scene, camera);

// Grab System
const grab = IWSDK.instance.getSystem('grab');
grab.makeGrabbable(object3D, config);

// Spatial Audio System
const spatialAudio = IWSDK.instance.getSystem('spatialAudio');
spatialAudio.initialize(camera);
```

## Testing the Integration

1. Start the backend server:
```bash
cd backend
python -m main
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Open your browser to http://localhost:3000

## Deployment

For production deployment, see `PRODUCTION_DEPLOYMENT.md` for complete instructions.

## Troubleshooting

- If IWSDK features don't work, check browser console for errors
- Ensure all required dependencies are installed
- Verify that the application is served over HTTPS for WebXR features
- Check that WebGL 2.0 is supported in the browser

## Future Enhancements

1. **Real IWSDK Integration**: Replace simulation layer with actual IWSDK packages when available
2. **VR/AR Support**: Full WebXR integration for head-mounted displays
3. **Multi-user Experiences**: Shared virtual shopping sessions
4. **Advanced AI Integration**: Real-time styling recommendations in 3D
5. **Blockchain Integration**: Virtual item ownership in 3D space
6. **Scene Understanding**: Automatic detection of real-world surfaces

## Contributing

We welcome contributions to enhance the IWSDK integration. Please follow the existing code patterns and ensure all new features include:

- Proper error handling
- Security considerations
- Performance optimization
- Test coverage
- Documentation updates

## License

This project is part of the Aetherstore Engine and is licensed under the same terms as the main project.