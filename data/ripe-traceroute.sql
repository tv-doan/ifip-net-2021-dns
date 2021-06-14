CREATE TABLE IF NOT EXISTS "traceroute" (
"msm_id" INTEGER,
  "timestamp" INTEGER,
  "method" TEXT,
  "probe_id" INTEGER,
  "addr_fam" INTEGER,
  "origin" TEXT,
  "src" TEXT,
  "dst" TEXT,
  "dst_name" TEXT,
  "status" TEXT,
  "ip_path_length" INTEGER,
  "ttl" INTEGER,
  "endpoint" TEXT,
  "rtt" REAL
);
