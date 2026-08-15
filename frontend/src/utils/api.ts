export const getBackendUrl = (path: string = "") => {
  const host = typeof window !== 'undefined' ? window.location.hostname : '127.0.0.1';
  return `http://${host}:8001${path}`;
};

export const getWsUrl = () => {
  const host = typeof window !== 'undefined' ? window.location.hostname : '127.0.0.1';
  return `ws://${host}:8001/ws/live`;
};
