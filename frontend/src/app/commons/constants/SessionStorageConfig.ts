export const SESSION_STORAGE_CLEANUP = [
  {
    key: 'app_error_message', //Key sessionstorage
    excludeRoutes: ['/error'], //patURL
  },
  {
    key: 'notFoundUrl',
    excludeRoutes: ['/not-found'],
  },
] as const;
