import http from 'k6/http';
import { check } from 'k6';
export const options = { vus: 500, duration: '30s' };
export default function () {
  const r = http.get('http://localhost:80/tiles/11/1200/770.png');
  check(r, {
    'status_200': s => s.status === 200,
    'status_404': s => s.status === 404,
    'status_400': s => s.status === 400,
    'status_408': s => s.status === 408,
    'status_429': s => s.status === 429,
    'status_500': s => s.status === 500,
    'status_502': s => s.status === 502,
    'status_503': s => s.status === 503,
    'status_504': s => s.status === 504,
    'status_other': s => ![200, 400, 404, 408, 429, 500, 502, 503, 504].includes(s.status),
  });
}
