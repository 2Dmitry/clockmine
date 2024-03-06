SELECT
    i.id,
    i.estimated_hours,
    tr."name" tracker_name,
    istat."name" status_name,
    u.lastname lastname
FROM
    issues i
    JOIN trackers tr ON tr.id = i.tracker_id
    JOIN issue_statuses istat ON istat.id = i.status_id
    JOIN users u ON u.id = i.assigned_to_id
WHERE
    i.project_id = 69 -- AND -- sber
    AND i.status_id NOT IN (5, 10)