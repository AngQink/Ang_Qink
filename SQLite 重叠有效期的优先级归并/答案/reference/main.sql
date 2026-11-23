WITH stream AS (
    SELECT rowid AS pos, *,
           SUM(CASE WHEN a=0 THEN 1 ELSE 0 END) OVER (ORDER BY rowid) AS session,
           MAX(CASE WHEN a=0 THEN rowid ELSE 0 END) OVER (ORDER BY rowid) AS origin
    FROM input
),
ranked AS (
    SELECT q.pos,w.c AS start,w.e AS val,w.f AS priority,
           row_number() OVER (PARTITION BY q.pos ORDER BY w.f DESC,w.d-w.c,w.pos DESC) AS n
    FROM stream q JOIN stream w ON w.session=q.session AND w.b=q.b AND w.pos<q.pos AND q.c>=w.c AND q.c<w.d
    WHERE q.a=2 AND w.a=1
)
SELECT n IS NOT NULL,coalesce(val,0),coalesce(priority,0),coalesce(start,0)
FROM stream LEFT JOIN ranked USING(pos) WHERE n IS NULL OR n=1
ORDER BY pos;
