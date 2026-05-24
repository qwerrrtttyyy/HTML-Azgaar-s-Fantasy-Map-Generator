# Fantasy Map Generator - Browser Ready Version

This folder contains a browser-ready build of Azgaar's Fantasy Map Generator.

## How to Use

### Option 1: Open directly in browser (may have CORS issues)
Simply open `index.html` in your web browser. Note that some features may not work due to browser security restrictions when opening local files.

### Option 2: Use a local web server (recommended)
Run a simple HTTP server in this directory:

**Python 3:**
```bash
cd browser-ready
python -m http.server 8000
```

**Node.js:**
```bash
npx serve browser-ready
```

**PHP:**
```bash
cd browser-ready
php -S localhost:8000
```

Then open `http://localhost:8000` in your browser.

## Files

- `index.html` - Main HTML file with all SVG definitions and UI
- `index-DMtDjmBV.js` - Bundled JavaScript application code
- `index-B3l7mx48.css` - Bundled CSS styles
- `libs/` - Third-party libraries (D3.js, jQuery, etc.)
- `modules/` - Application modules
- `images/` - Image assets
- `styles/` - Map style presets (JSON)
- `config/` - Configuration files
- And other supporting files

## Notes

- This is a pre-built version from the source code
- The application uses modern JavaScript features and requires a recent browser
- For the best experience, use Chrome, Firefox, or Edge
- Some features like service workers and IndexedDB require HTTPS or localhost
