WITH stream AS (
    SELECT rowid AS pos, *,
           SUM(CASE WHEN a=0 THEN 1 ELSE 0 END) OVER (ORDER BY rowid) AS session,
           MAX(CASE WHEN a=0 THEN rowid ELSE 0 END) OVER (ORDER BY rowid) AS origin
    FROM input
),
gaps AS (
    SELECT *, c-lag(c) OVER (PARTITION BY session,b ORDER BY c,pos) AS gap FROM stream WHERE a=1
), cuts AS (
    SELECT *,sum(CASE WHEN gap IS NULL OR gap>8 THEN 1 ELSE 0 END)
          OVER (PARTITION BY session,b ORDER BY c,pos) AS segment
    FROM gaps
), spans AS (
    SELECT pos,segment,count(*) OVER grp AS items,sum(d) OVER grp AS total,min(c) OVER grp AS first
    FROM cuts WINDOW grp AS (PARTITION BY session,b,segment)
)
SELECT coalesce(segment,0),coalesce(items,0),coalesce(total,0),coalesce(first,0)
FROM stream LEFT JOIN spans USING(pos) ORDER BY pos;
