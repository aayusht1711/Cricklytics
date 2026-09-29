export const getBackendUrl = (path: string = "") => {
  const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${cleanPath}`;
};

export const getWsUrl = () => {
  if (process.env.NEXT_PUBLIC_BACKEND_URL) {
    const wsBase = process.env.NEXT_PUBLIC_BACKEND_URL.replace(/^http/, 'ws');
    return `${wsBase}/ws/live-match`;
  }
  const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
  return `ws://${host}:8000/ws/live-match`;
};
