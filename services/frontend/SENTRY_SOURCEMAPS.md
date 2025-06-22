# Sentry Source Maps Configuration

This document explains how source maps are configured for the Angular frontend to work with Sentry.

## Development vs Production Modes

### Development Mode
When running with `./start-dev.sh` or `docker-compose.dev.yml`:
- Source maps are inline and always available
- Full stack traces visible in browser console
- Sentry debug mode enabled (verbose logging)
- Hot reload enabled for faster development

### Production Mode  
When running with `./start.sh` or standard `docker-compose.yml`:
- Source maps are generated as separate files
- Only loaded when DevTools are open
- Debug mode disabled
- Optimized build with minification

## What's Already Configured

### 1. Angular Build Configuration
- Source maps are enabled in production builds (`angular.json`)
- Configuration includes all necessary map types (scripts, styles, vendor)
- Maps are not hidden, making them accessible for debugging

### 2. Sentry SDK Configuration
- Release tracking is configured to match source maps with errors
- Debug mode is disabled in production
- Proper error handling for source map references

## How to Upload Source Maps to Sentry

### Option 1: Manual Upload (Development/Testing)

1. Install Sentry CLI:
```bash
npm install -g @sentry/cli
```

2. Configure authentication:
```bash
# Set your auth token (get from Sentry dashboard)
export SENTRY_AUTH_TOKEN=your-token-here
```

3. Build the application:
```bash
npm run build
```

4. Upload source maps:
```bash
sentry-cli releases new 1.0.0
sentry-cli releases files 1.0.0 upload-sourcemaps ./dist/frontend --url-prefix ~/
sentry-cli releases finalize 1.0.0
```

### Option 2: Automated Upload (CI/CD)

Add to your CI/CD pipeline:

```yaml
# Example for GitHub Actions
- name: Upload Source Maps
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: your-org
    SENTRY_PROJECT: your-project
  run: |
    npm run build
    npx @sentry/cli releases new ${{ github.sha }}
    npx @sentry/cli releases files ${{ github.sha }} upload-sourcemaps ./dist/frontend --url-prefix ~/
    npx @sentry/cli releases finalize ${{ github.sha }}
```

### Option 3: Webpack Plugin (Alternative)

For more automated integration, you can use the Sentry Webpack plugin:

```bash
npm install --save-dev @sentry/webpack-plugin
```

Then configure in your build process (requires ejecting from Angular CLI or using custom webpack config).

## Production Considerations

### Performance Impact
- **Build Time**: Source map generation adds ~10-20% to build time
- **Bundle Size**: Source maps are separate files, not included in main bundles
- **Network**: Maps are only downloaded when DevTools are open
- **Security**: Consider using hidden source maps in production

### Security Recommendations

1. **Hidden Source Maps** (More Secure):
```json
"sourceMap": {
  "scripts": true,
  "styles": false,
  "hidden": true,
  "vendor": false
}
```

2. **Upload and Delete**:
- Upload maps to Sentry
- Delete them from public server
- Sentry will use uploaded maps for error processing

3. **Access Control**:
- Serve source maps only to authorized IPs
- Use authentication for map endpoints

## Verifying Source Maps Work

1. Trigger an error in production
2. Check Sentry dashboard
3. Look for:
   - Proper file names (not minified)
   - Correct line numbers
   - Original source code visible

## Troubleshooting

### Common Issues:

1. **"Source code was not found"**
   - Ensure release versions match
   - Check URL prefix in upload command
   - Verify maps are accessible at expected URLs

2. **Wrong line numbers**
   - Rebuild with clean cache
   - Ensure no post-processing after build
   - Check for source map comments in JS files

3. **Missing context**
   - Enable vendor source maps if needed
   - Include all chunk maps in upload

## Current Configuration Summary

✅ Source maps enabled for production builds
✅ Release tracking configured
✅ Proper URL patterns set
✅ Debug mode disabled in production
⚠️ Manual upload required (not automated yet)

## Next Steps

1. Set up Sentry organization and project
2. Get authentication token
3. Configure CI/CD for automatic uploads
4. Test with real production deployment