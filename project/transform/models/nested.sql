SELECT 
    sample_one.id,
    sample_one.first_name,
    sample_one.last_name
FROM
    {{ source("tap_csv", "sample_one") }}
CROSS JOIN
    {{ source("tap_csv", "sample_two") }}
