import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 10,
    duration: '10s',

    summaryTrendStats: [
        'avg',
        'min',
        'med',
        'max',
        'p(50)',
        'p(90)',
        'p(95)',
        'p(99)',
    ],
};

export default function () {

    // -------------------------
    // POST /shorten
    // -------------------------

    const payload = JSON.stringify({
        url: `https://example${__VU}-${__ITER}.com`
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const shortenResponse = http.post(
        'http://127.0.0.1:8000/shorten',
        payload,
        params
    );

    check(shortenResponse, {
        'shorten status is 201': (r) => r.status === 201,
    });

    const shortCode = shortenResponse.json('short_code');

    // -------------------------
    // GET /redirect
    // -------------------------

    const redirectResponse = http.get(
        `http://127.0.0.1:8000/redirect?code=${shortCode}`,
        {
            redirects: 0,
        }
    );

    check(redirectResponse, {
        'redirect status is 302': (r) => r.status === 302,
    });

    sleep(1);
}