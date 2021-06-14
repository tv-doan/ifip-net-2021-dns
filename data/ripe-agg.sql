CREATE TABLE IF NOT EXISTS "dns" (
"msm_id" INTEGER,
  "timestamp" TIMESTAMP,
  "probe_id" INTEGER,
  "country" TEXT,
  "continent" TEXT,
  "address_family" INTEGER,
  "resolver_address" TEXT,
  "resolver_name" TEXT,
  "local_resolver" INTEGER,
  "target_name" TEXT,
  "response_type" TEXT,
  "response_address" TEXT,
  "rt" REAL,
  "ttl" REAL
);
CREATE TABLE IF NOT EXISTS "traceroute" (
"msm_id" INTEGER,
  "timestamp" TIMESTAMP,
  "method" TEXT,
  "probe_id" INTEGER,
  "country" TEXT,
  "continent" TEXT,
  "addr_fam" INTEGER,
  "origin" TEXT,
  "src" TEXT,
  "dst" TEXT,
  "dst_name" TEXT,
  "resolver_name" TEXT,
  "status" TEXT,
  "ip_path_length" INTEGER,
  "ttl" INTEGER,
  "endpoint" TEXT,
  "rtt" REAL
);
CREATE TABLE IF NOT EXISTS "traceroute_as" (
"msm_id" REAL,
  "timestamp" TIMESTAMP,
  "method" TEXT,
  "probe_id" REAL,
  "country" TEXT,
  "continent" TEXT,
  "addr_fam" REAL,
  "origin" TEXT,
  "src" TEXT,
  "dst" TEXT,
  "dst_name" TEXT,
  "resolver_name" TEXT,
  "status" TEXT,
  "ip_path_length" REAL,
  "ttl" REAL,
  "endpoint" TEXT,
  "rtt" REAL,
  "asn" REAL,
  "holder" TEXT,
  "as_hop" REAL
);
