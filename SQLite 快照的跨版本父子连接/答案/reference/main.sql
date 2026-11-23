WITH stream AS (
    SELECT rowid AS pos, *,
           SUM(CASE WHEN a=0 THEN 1 ELSE 0 END) OVER (ORDER BY rowid) AS session,
           MAX(CASE WHEN a=0 THEN rowid ELSE 0 END) OVER (ORDER BY rowid) AS origin
    FROM input
),
children AS (
    SELECT q.pos,q.session,w.c AS rev,w.d AS parent,w.e AS value,
           row_number() OVER (PARTITION BY q.pos ORDER BY w.c DESC,w.pos DESC) AS n
    FROM stream q JOIN stream w ON w.session=q.session AND w.b=q.b AND w.pos<q.pos AND w.c<=q.c
    WHERE q.a=3 AND w.a=2
), parents AS (
    SELECT c.pos,w.d AS weight,w.e AS deleted,
           row_number() OVER (PARTITION BY c.pos ORDER BY w.c DESC,w.pos DESC) AS n
    FROM children c JOIN stream w ON w.session=c.session AND w.b=c.parent AND w.pos<c.pos AND w.c<=c.rev
    WHERE c.n=1 AND w.a=1
)
SELECT (c.n IS NOT NULL)+(p.n IS NOT NULL),coalesce(c.rev,0),coalesce(p.weight,0),
       coalesce(c.value,0)+coalesce(p.weight,0)
FROM stream q LEFT JOIN children c ON c.pos=q.pos AND c.n=1
LEFT JOIN parents p ON p.pos=q.pos AND p.n=1 AND p.deleted=0
ORDER BY q.pos;
