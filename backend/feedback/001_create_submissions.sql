CREATE TABLE IF NOT EXISTS submissions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('bug_report', 'feedback')),
    title TEXT NOT NULL CHECK (length(btrim(title)) BETWEEN 1 AND 160),
    message TEXT NOT NULL CHECK (length(message) BETWEEN 1 AND 4000),
    severity TEXT CHECK (severity IS NULL OR severity IN ('critical', 'major', 'minor', 'unspecified')),
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'reviewed', 'resolved', 'ignored')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT submissions_type_severity_check CHECK (
        (type = 'bug_report' AND severity IS NOT NULL)
        OR (type = 'feedback' AND severity IS NULL)
    )
);

CREATE INDEX IF NOT EXISTS submissions_created_at_idx ON submissions (created_at DESC);
CREATE INDEX IF NOT EXISTS submissions_status_idx ON submissions (status, created_at DESC);

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

CREATE INDEX IF NOT EXISTS changelog_entries_created_at_idx ON changelog_entries (created_at DESC);
CREATE INDEX IF NOT EXISTS changelog_submission_links_submission_idx ON changelog_submission_links (submission_id);
