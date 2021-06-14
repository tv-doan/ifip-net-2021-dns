CREATE TABLE IF NOT EXISTS "metadata" (
"address_v4" TEXT,
  "address_v6" TEXT,
  "asn_v4" REAL,
  "asn_v6" REAL,
  "country_code" TEXT,
  "description" TEXT,
  "first_connected" INTEGER,
  "geometry" TEXT,
  "id" INTEGER,
  "is_anchor" INTEGER,
  "is_public" INTEGER,
  "last_connected" INTEGER,
  "prefix_v4" TEXT,
  "prefix_v6" TEXT,
  "status" TEXT,
  "status_since" INTEGER,
  "tags" TEXT,
  "total_uptime" INTEGER,
  "type" TEXT
);
