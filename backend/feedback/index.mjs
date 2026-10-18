import pg from 'pg';
import { timingSafeEqual } from 'node:crypto';

const { Pool } = pg;
const pool = new Pool({ connectionString: process.env.DATABASE_URL, max: 5 });

function hasAdminAccess(request) {
  const expected = process.env.FEEDBACK_ADMIN_TOKEN;
  const authorization = request.headers.get('authorization') || '';
  const provided = authorization.match(/^Bearer\s+(.+)$/i)?.[1];
  if (!expected || !provided) return false;

  const expectedBytes = Buffer.from(expected);
  const providedBytes = Buffer.from(provided);
  return expectedBytes.length === providedBytes.length && timingSafeEqual(expectedBytes, providedBytes);
}

export default async function fetch(request) {
  if (request.method === 'GET') {
    if (!process.env.FEEDBACK_ADMIN_TOKEN) {
      return Response.json({ error: 'Admin access is not configured' }, { status: 503 });
    }
    if (!hasAdminAccess(request)) {
      return Response.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const requestedType = new URL(request.url).searchParams.get('type') || 'all';
    if (!['all', 'bug_report', 'suggestion'].includes(requestedType)) {
      return Response.json({ error: 'Invalid submission type' }, { status: 400 });
    }

    try {
      const type = requestedType === 'all' ? null : requestedType;
      const result = await pool.query(
        `SELECT id, type, message, status, created_at
         FROM submissions
         WHERE ($1::text IS NULL OR type = $1)
         ORDER BY created_at DESC
         LIMIT 500`,
        [type],
      );
      return Response.json({ submissions: result.rows });
    } catch (error) {
      console.error('Feedback list failed:', error);
      return Response.json({ error: 'Could not load submissions' }, { status: 500 });
    }
  }

  if (request.method !== 'POST') {
    return Response.json({ error: 'Method not allowed' }, { status: 405 });
  }

  const contentLength = Number(request.headers.get('content-length') || 0);
  if (contentLength > 16_384) {
    return Response.json({ error: 'Request too large' }, { status: 413 });
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  const { type, message } = body ?? {};
  if (!['bug_report', 'suggestion'].includes(type)) {
    return Response.json({ error: 'Invalid submission type' }, { status: 400 });
  }
  if (typeof message !== 'string' || !message.trim() || message.length > 4000) {
    return Response.json({ error: 'Message must be between 1 and 4000 characters' }, { status: 400 });
  }

  try {
    await pool.query('INSERT INTO submissions (type, message) VALUES ($1, $2)', [type, message.trim()]);
    return Response.json({ ok: true }, { status: 201 });
  } catch (error) {
    console.error('Feedback submission failed:', error);
    return Response.json({ error: 'Could not save submission' }, { status: 500 });
  }
}
