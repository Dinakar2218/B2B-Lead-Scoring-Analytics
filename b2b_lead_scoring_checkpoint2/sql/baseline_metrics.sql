-- Overall funnel health
SELECT COUNT(*) AS total_leads,
       SUM(converted) AS converted_leads,
       ROUND(100.0 * AVG(converted), 2) AS conversion_rate_pct,
       ROUND(AVG(response_time_hours), 2) AS avg_response_hours,
       ROUND(AVG(number_of_rfqs), 2) AS avg_rfqs
FROM leads_clean;

-- Segment performance
SELECT industry, company_size, COUNT(*) AS leads,
       ROUND(100.0 * AVG(converted), 2) AS conversion_rate_pct
FROM leads_clean
GROUP BY industry, company_size
ORDER BY conversion_rate_pct DESC;

-- Monthly trend
SELECT created_month, COUNT(*) AS leads,
       SUM(converted) AS conversions,
       ROUND(100.0 * AVG(converted), 2) AS conversion_rate_pct
FROM leads_clean
GROUP BY created_month
ORDER BY created_month;

