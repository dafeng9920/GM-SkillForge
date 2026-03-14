import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '../dist');
const port = Number(process.env.PORT || 4173);

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.ico': 'image/x-icon',
  '.map': 'application/json; charset=utf-8',
};

if (!fs.existsSync(root)) {
  console.error('dist directory does not exist. Run `npm run build` first.');
  process.exit(1);
}

const server = http.createServer((request, response) => {
  const requestPath = new URL(request.url || '/', `http://${request.headers.host}`).pathname;
  const normalizedPath = requestPath === '/' ? '/index.html' : requestPath;
  let filePath = path.join(root, normalizedPath);

  if (!filePath.startsWith(root)) {
    response.writeHead(403);
    response.end('Forbidden');
    return;
  }

  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    filePath = path.join(root, 'index.html');
  }

  fs.readFile(filePath, (error, data) => {
    if (error) {
      response.writeHead(500);
      response.end('Internal Server Error');
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    response.writeHead(200, {
      'Content-Type': mimeTypes[ext] || 'application/octet-stream',
      'Cache-Control': 'no-cache',
    });
    response.end(data);
  });
});

server.listen(port, '127.0.0.1', () => {
  console.log(`Serving dist on http://127.0.0.1:${port}`);
});
