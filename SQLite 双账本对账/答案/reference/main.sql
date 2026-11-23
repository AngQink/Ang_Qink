WITH stream AS (
    SELECT rowid AS pos, *,
           SUM(CASE WHEN a=0 THEN 1 ELSE 0 END) OVER (ORDER BY rowid) AS session,
           MAX(CASE WHEN a=0 THEN rowid ELSE 0 END) OVER (ORDER BY rowid) AS origin
    FROM input
),
ranked AS (
    SELECT q.pos,w.a AS side,w.d AS amount,w.e AS deleted,
           row_number() OVER (PARTITION BY q.pos,w.a ORDER BY w.c DESC,w.pos DESC) AS n
    FROM stream q JOIN stream w ON w.session=q.session AND w.b=q.b AND w.pos<q.pos AND w.c<=q.c
    WHERE q.a=3 AND w.a IN (1,2)
), amounts AS (
    SELECT q.pos,l.amount AS left_amount,r.amount AS right_amount
    FROM stream q
    LEFT JOIN ranked l ON l.pos=q.pos AND l.side=1 AND l.n=1 AND l.deleted=0
    LEFT JOIN ranked r ON r.pos=q.pos AND r.side=2 AND r.n=1 AND r.deleted=0
)
SELECT (left_amount IS NOT NULL)+2*(right_amount IS NOT NULL),coalesce(left_amount,0),
       coalesce(right_amount,0),coalesce(left_amount,0)-coalesce(right_amount,0)
FROM amounts ORDER BY pos;
