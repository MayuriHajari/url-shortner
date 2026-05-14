import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 10,
    iterations: 10,
};

export default function () {

    // -------------------------
    // POST /shorten
    // -------------------------

    const payload = JSON.stringify({
        url: `https://example${__ITER}.com`
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