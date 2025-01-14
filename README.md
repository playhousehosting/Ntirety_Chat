# Ntirety Chatbot - Vercel/Cloudflare Version

This is a version of the Ntirety Chatbot optimized for deployment on Vercel and Cloudflare.

## Environment Variables

Set the following environment variables in your deployment platform:

- `DIFY_BASE_URL`: Your Dify API base URL
- `DIFY_API_KEY`: Your Dify API key

## Deployment Instructions

### Vercel Deployment

1. Install the Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy the application:
```bash
vercel
```

4. Set environment variables:
```bash
vercel env add DIFY_BASE_URL
vercel env add DIFY_API_KEY
```

### Cloudflare Pages Deployment

1. Create a new Pages project in Cloudflare Dashboard
2. Connect your repository
3. Set build settings:
   - Build command: `pip install -r requirements.txt && streamlit run app.py`
   - Build output directory: Not required
4. Add environment variables in the Cloudflare Dashboard:
   - `DIFY_BASE_URL`
   - `DIFY_API_KEY`

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Key Changes from Original Version

1. Environment variable support for API configuration
2. Simplified file structure
3. Vercel-specific configuration
4. Removed system-specific dependencies
5. Optimized for serverless deployment
