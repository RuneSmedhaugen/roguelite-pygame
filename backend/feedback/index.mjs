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

function jsonError(message, status) {
  return Response.json({ error: message }, { status });
}

export default async function fetch(request) {
  const path = new URL(request.url).pathname.replace(/\/+$/, '') || '/';
  const isAdmin = hasAdminAccess(request);

  if (request.method === 'GET' && path === '/changelog') {
    try {
      const result = isAdmin
        ? await pool.query(`
            SELECT e.id, e.title, e.body, e.created_at,
                   COALESCE(json_agg(json_build_object('id', s.id, 'title', s.title, 'type', s.type)
                     ORDER BY s.id) FILTER (WHERE s.id IS NOT NULL), '[]') AS tickets
            FROM changelog_entries e
            LEFT JOIN changelog_submission_links l ON l.changelog_id = e.id
            LEFT JOIN submissions s ON s.id = l.submission_id
            GROUP BY e.id
            ORDER BY e.created_at DESC
            LIMIT 200`)
        : await pool.query(`
            SELECT id, title, body, created_at
            FROM changelog_entries
            ORDER BY created_at DESC
            LIMIT 100`);
      return Response.json({ entries: result.rows });
    } catch (error) {
      console.error('Changelog load failed:', error);
      return jsonError('Could not load changelog', 500);
    }
  }

  if (request.method === 'GET' && path === '/') {
    if (!process.env.FEEDBACK_ADMIN_TOKEN) return jsonError('Admin access is not configured', 503);
    if (!isAdmin) return jsonError('Unauthorized', 401);
    const requestedType = new URL(request.url).searchParams.get('type') || 'all';
    if (!['all', 'bug_report', 'feedback'].includes(requestedType)) {
      return jsonError('Invalid submission type', 400);
    }
    try {
      const type = requestedType === 'all' ? null : requestedType;
      const result = await pool.query(
        `SELECT id, type, title, message, severity, status, created_at
         FROM submissions
         WHERE ($1::text IS NULL OR type = $1)
         ORDER BY created_at DESC
         LIMIT 500`,
        [type],
      );
      return Response.json({ submissions: result.rows });
    } catch (error) {
      console.error('Feedback list failed:', error);
      return jsonError('Could not load submissions', 500);
    }
  }

  if (request.method !== 'POST') return jsonError('Method not allowed', 405);
  const contentLength = Number(request.headers.get('content-length') || 0);
  if (contentLength > 32_768) return jsonError('Request too large', 413);

  let body;
  try {
    body = await request.json();
  } catch {
    return jsonError('Invalid JSON', 400);
  }

  if (path === '/changelog') {
    if (!process.env.FEEDBACK_ADMIN_TOKEN) return jsonError('Admin access is not configured', 503);
    if (!isAdmin) return jsonError('Unauthorized', 401);
    const title = typeof body?.title === 'string' ? body.title.trim() : '';
    const text = typeof body?.body === 'string' ? body.body.trim() : '';
    const submissionIds = body?.submissionIds;
    if (!title || title.length > 160) return jsonError('Title must be between 1 and 160 characters', 400);
    if (!text || text.length > 10_000) return jsonError('Details must be between 1 and 10000 characters', 400);
    if (!Array.isArray(submissionIds) || submissionIds.length > 100
        || submissionIds.some((id) => !Number.isSafeInteger(Number(id)) || Number(id) < 1)) {
      return jsonError('Ticket links are invalid', 400);
    }

    const client = await pool.connect();
    try {
      await client.query('BEGIN');
      const entry = await client.query(
        'INSERT INTO changelog_entries (title, body) VALUES ($1, $2) RETURNING id',
        [title, text],
      );
      const id = entry.rows[0].id;
      const uniqueIds = [...new Set(submissionIds.map(Number))];
      if (uniqueIds.length) {
        const existing = await client.query(
          'SELECT id FROM submissions WHERE id = ANY($1::bigint[])', [uniqueIds],
        );
        if (existing.rowCount !== uniqueIds.length) {
          await client.query('ROLLBACK');
          return jsonError('One or more linked tickets could not be found', 400);
        }
        await client.query(
          'INSERT INTO changelog_submission_links (changelog_id, submission_id) SELECT $1, linked_id FROM unnest($2::bigint[]) AS linked(linked_id)',
          [id, uniqueIds],
        );
      }
      await client.query('COMMIT');
      return Response.json({ ok: true, id }, { status: 201 });
    } catch (error) {
      await client.query('ROLLBACK');
      console.error('Changelog publish failed:', error);
      return jsonError('Could not publish changelog entry', 500);
    } finally {
      client.release();
    }
  }

  if (path !== '/') return jsonError('Not found', 404);
  const { type, title: rawTitle, message, severity } = body ?? {};
  const title = typeof rawTitle === 'string' ? rawTitle.trim() : '';
  if (!['bug_report', 'feedback'].includes(type)) return jsonError('Invalid submission type', 400);
  if (!title || title.length > 160) return jsonError('Title must be between 1 and 160 characters', 400);
  if (typeof message !== 'string' || !message.trim() || message.length > 4000) {
    return jsonError('Message must be between 1 and 4000 characters', 400);
  }
  if (type === 'bug_report' && !['critical', 'major', 'minor'].includes(severity)) {
    return jsonError('Choose a bug severity', 400);
  }
  if (type === 'feedback' && severity != null) return jsonError('Feedback cannot have a bug severity', 400);

  try {
    await pool.query(
      'INSERT INTO submissions (type, title, message, severity) VALUES ($1, $2, $3, $4)',
      [type, title, message.trim(), type === 'bug_report' ? severity : null],
    );
    return Response.json({ ok: true }, { status: 201 });
  } catch (error) {
    console.error('Feedback submission failed:', error);
    return jsonError('Could not save submission', 500);
  }
}
