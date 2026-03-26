// In production, we must use HTTPS to avoid Mixed Content errors.
// Also ensure no trailing slash in the base URL to prevent double slashes in fetch calls.
const rawUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
let sanitizedUrl = rawUrl.trim();
if (sanitizedUrl.endsWith('/')) {
  sanitizedUrl = sanitizedUrl.slice(0, -1);
}

// Special case: If we're on the user's production domain, force https strictly.
if (sanitizedUrl.includes('up.railway.app') && sanitizedUrl.startsWith('http:')) {
  sanitizedUrl = sanitizedUrl.replace('http:', 'https:');
}

export const API_URL = (sanitizedUrl.includes('localhost') || sanitizedUrl.includes('127.0.0.1')) 
  ? (sanitizedUrl.startsWith('http') ? sanitizedUrl : `http://${sanitizedUrl}`)
  : (sanitizedUrl.startsWith('https') ? sanitizedUrl : (sanitizedUrl.startsWith('http') ? sanitizedUrl.replace('http://', 'https://') : `https://${sanitizedUrl}`));
