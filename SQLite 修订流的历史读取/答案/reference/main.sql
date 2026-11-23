WITH stream AS (
    SELECT rowid AS pos, *,
           SUM(CASE WHEN a=0 THEN 1 ELSE 0 END) OVER (ORDER BY rowid) AS session,
           MAX(CASE WHEN a=0 THEN rowid ELSE 0 END) OVER (ORDER BY rowid) AS origin
    FROM input
),
ranked AS (
    SELECT q.pos,w.c AS rev,w.d AS val,w.e AS deleted,w.pos-w.origin AS arrival,
           row_number() OVER (PARTITION BY q.pos ORDER BY w.c DESC,w.pos DESC) AS n
    FROM stream q JOIN stream w ON w.session=q.session AND w.b=q.b AND w.pos<q.pos AND w.c<=q.c
    WHERE q.a=2 AND w.a=1
)
SELECT CASE WHEN r.n IS NULL THEN 0 WHEN r.deleted=1 THEN 2 ELSE 1 END,
       CASE WHEN r.deleted=0 THEN r.val ELSE 0 END, coalesce(r.rev,0), coalesce(r.arrival,0)
FROM stream q LEFT JOIN ranked r ON r.pos=q.pos AND r.n=1 ORDER BY q.pos;
