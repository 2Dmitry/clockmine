WITH tasks AS (
    SELECT
        i.id
    FROM
        issues i
    WHERE
        i.project_id = 69
        AND i.status_id NOT IN (5, 10)
)
SELECT
    ir.issue_from_id,
    ir.issue_to_id
FROM
    issue_relations ir
WHERE
    ir.relation_type = 'blocks'
    AND (
        ir.issue_from_id IN (
            SELECT
                t.id
            FROM
                tasks t
        )
        OR ir.issue_to_id IN (
            SELECT
                t.id
            FROM
                tasks t
        )
    )