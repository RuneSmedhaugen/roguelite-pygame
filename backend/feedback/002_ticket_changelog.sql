ALTER TABLE submissions ADD COLUMN IF NOT EXISTS title TEXT;
UPDATE submissions
SET title = left(regexp_replace(message, '\s+', ' ', 'g'), 100)
WHERE title IS NULL OR btrim(title) = '';
ALTER TABLE submissions ALTER COLUMN title SET NOT NULL;

ALTER TABLE submissions ADD COLUMN IF NOT EXISTS severity TEXT;
UPDATE submissions SET severity = 'unspecified'
WHERE type = 'bug_report' AND severity IS NULL;

ALTER TABLE submissions DROP CONSTRAINT IF EXISTS submissions_type_check;
UPDATE submissions SET type = 'feedback' WHERE type = 'suggestion';
ALTER TABLE submissions ADD CONSTRAINT submissions_type_check
    CHECK (type IN ('bug_report', 'feedback'));

ALTER TABLE submissions DROP CONSTRAINT IF EXISTS submissions_severity_check;
ALTER TABLE submissions ADD CONSTRAINT submissions_severity_check
    CHECK (severity IS NULL OR severity IN ('critical', 'major', 'minor', 'unspecified'));
ALTER TABLE submissions DROP CONSTRAINT IF EXISTS submissions_type_severity_check;
ALTER TABLE submissions ADD CONSTRAINT submissions_type_severity_check
    CHECK ((type = 'bug_report' AND severity IS NOT NULL)
        OR (type = 'feedback' AND severity IS NULL));

CREATE TABLE IF NOT EXISTS changelog_entries (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL CHECK (length(btrim(title)) BETWEEN 1 AND 160),
    body TEXT NOT NULL CHECK (length(btrim(body)) BETWEEN 1 AND 10000),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS changelog_submission_links (
    changelog_id BIGINT NOT NULL REFERENCES changelog_entries(id) ON DELETE CASCADE,
    submission_id BIGINT NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    PRIMARY KEY (changelog_id, submission_id)
);

CREATE INDEX IF NOT EXISTS changelog_entries_created_at_idx
    ON changelog_entries (created_at DESC);
CREATE INDEX IF NOT EXISTS changelog_submission_links_submission_idx
    ON changelog_submission_links (submission_id);
