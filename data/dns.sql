CREATE TABLE IF NOT EXISTS "data" (
"msm_id" INTEGER,
  "prb_id" INTEGER,
  "timestamp" TIMESTAMP,
  "resolver_address" TEXT,
  "address_family" INTEGER,
  "rt" REAL,
  "error" TEXT,
  "local_resolver" INTEGER,
  "abuf" TEXT,
  "target_name" TEXT,
  "rcode" TEXT,
  "response_type" TEXT,
  "response_address" TEXT,
  "ttl" REAL,
  "target_name_meta" TEXT,
  "response_af" INTEGER,
  "resolver_af" INTEGER
);
