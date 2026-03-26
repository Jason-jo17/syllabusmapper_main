const rawUrl = process.env.NEXT_PUBLIC_API_URL || "https://syllabusmappermain-production.up.railway.app";
// Force https unless it's localhost or already specified with http (but we prefer https for production)
export const API_URL = (rawUrl.includes('localhost') || rawUrl.includes('127.0.0.1')) 
  ? (rawUrl.startsWith('http') ? rawUrl : `http://${rawUrl}`)
  : (rawUrl.startsWith('https') ? rawUrl : (rawUrl.startsWith('http') ? rawUrl.replace('http://', 'https://') : `https://${rawUrl}`));
