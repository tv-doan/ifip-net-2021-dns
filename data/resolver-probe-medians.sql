CREATE TABLE IF NOT EXISTS "heatmap_v4" (
"probe_id" INTEGER,
  "CleanBrowsing" REAL,
  "Cloudflare" REAL,
  "Google" REAL,
  "Neustar" REAL,
  "NextDNS" REAL,
  "OpenDNS" REAL,
  "OpenNIC" REAL,
  "Quad9" REAL,
  "VeriSign" REAL,
  "Yandex" REAL,
  "continent" TEXT,
  "country" TEXT,
  "local" REAL,
  "probe_count_continent" INTEGER
);
CREATE INDEX "ix_heatmap_v4_probe_id"ON "heatmap_v4" ("probe_id");
CREATE TABLE IF NOT EXISTS "heatmap_v6" (
"probe_id" INTEGER,
  "CleanBrowsing" REAL,
  "Cloudflare" REAL,
  "Google" REAL,
  "Neustar" REAL,
  "NextDNS" REAL,
  "OpenDNS" REAL,
  "OpenNIC" REAL,
  "Quad9" REAL,
  "VeriSign" REAL,
  "Yandex" REAL,
  "continent" TEXT,
  "country" TEXT,
  "local" REAL,
  "probe_count_continent" INTEGER
);
CREATE INDEX "ix_heatmap_v6_probe_id"ON "heatmap_v6" ("probe_id");
