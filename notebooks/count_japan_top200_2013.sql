SELECT COUNT(*) AS japan_top200_2013
FROM university_rankings
WHERE country = 'Japan' AND year = 2013 AND world_rank <= 200;
