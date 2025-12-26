/* const { env } = require('process');
const target = env.ASPNETCORE_HTTPS_PORT ? `https://localhost:${env.ASPNETCORE_HTTPS_PORT}` :
  env.ASPNETCORE_URLS ? env.ASPNETCORE_URLS.split(';')[0] : 'https://localhost:7133';

const PROXY_CONFIG = [
  {
     context: [
      "/api/Reporte/generate-acta",
      "/api/Reporte/generate-acta",
      "/api/Reporte/generate-report-observations",
      "/api/Shared/listarPeriodos",
      "/api/Shared/listaGmrByPeriodo",
      "/api/Shared/listUdrByPeriodAndGmr",
      "/api/Shared/listUeByPeriodAndGmrAndUdr",
      "/api/v1/auth/login",
      "/api/Auth/logout",
    ], 
    target,
    secure: false,
    changeOrigin: true,
    rejectUnauthorized: false
  }
]
module.exports = PROXY_CONFIG;
 */