const rawUrl = process.env.NEXT_PUBLIC_API_URL || "https://syllabusmappermain-production.up.railway.app";
export const API_URL = rawUrl.startsWith('http') ? rawUrl : `https://${rawUrl}`;
