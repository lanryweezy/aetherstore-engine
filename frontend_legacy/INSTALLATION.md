# Installation Guide - Futuristic UI Setup

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This will install:
- Tailwind CSS 3.4.0
- PostCSS & Autoprefixer
- All existing dependencies

### 2. Build for Development

```bash
npm start
```

This starts the webpack dev server on `http://localhost:3000`

### 3. Build for Production

```bash
npm run build
```

This creates optimized production bundles in the `dist/` directory.

## 📁 File Structure

```
frontend/
├── styles/
│   ├── tailwind.css          # Main Tailwind file with custom components
│   └── main.css              # Legacy styles (can be removed)
├── tailwind.config.js        # Tailwind configuration
├── postcss.config.js         # PostCSS configuration
├── webpack.config.js          # Webpack config (updated for Tailwind)
├── index.html                # Main HTML (updated with Tailwind)
└── admin/
    └── index.html            # Admin dashboard (updated with Tailwind)
```

## 🎨 Using the Design System

### Import Tailwind CSS

In your HTML files, include:

```html
<link rel="stylesheet" href="styles/tailwind.css">
```

### Use Component Classes

```html
<!-- Buttons -->
<button class="btn btn-neon">Neon Button</button>
<button class="btn btn-hologram">Holographic Button</button>

<!-- Cards -->
<div class="card-glow">
  <div class="card-body">Content</div>
</div>

<!-- Text Effects -->
<h1 class="gradient-text-glow">Futuristic Text</h1>
```

See `DESIGN_SYSTEM.md` for complete component documentation.

## 🔧 Configuration

### Customizing Colors

Edit `tailwind.config.js`:

```js
colors: {
  neon: {
    yourColor: '#your-hex',
  }
}
```

### Adding Custom Animations

Edit `tailwind.config.js` keyframes:

```js
keyframes: {
  yourAnimation: {
    '0%': { /* start */ },
    '100%': { /* end */ },
  }
}
```

## 🐛 Troubleshooting

### Tailwind classes not working?

1. Make sure `postcss-loader` is in webpack config
2. Check that `tailwind.css` is imported
3. Verify `tailwind.config.js` content paths are correct
4. Rebuild: `npm run build`

### Styles not updating?

1. Clear browser cache
2. Restart dev server
3. Check webpack is watching CSS files

### Build errors?

1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Check Node.js version (16+ required)

## 📚 Next Steps

1. Read `DESIGN_SYSTEM.md` for component usage
2. Customize colors in `tailwind.config.js`
3. Add your own components in `styles/tailwind.css`
4. Build your futuristic UI! 🚀

