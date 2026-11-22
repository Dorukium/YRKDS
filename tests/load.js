import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '5s', target: 100 },
    { duration: '20s', target: 100 },
    { duration: '5s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<300'],
    http_req_failed: ['rate<0.01'],
  },
};

const POLY = JSON.stringify({
  geojson: {
    type: 'Polygon',
    coordinates: [[[30.640, 36.880], [30.642, 36.880], [30.642, 36.882],
                   [30.640, 36.882], [30.640, 36.880]]],
  },
});

export default function () {
  const r = http.post('http://localhost:8000/api/analyze', POLY, {
    headers: { 'Content-Type': 'application/json' },
  });
  check(r, { 'status 200': (res) => res.status === 200 });
}
