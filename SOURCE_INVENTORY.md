# Source inventory and coverage

**Exhaustive semantic investigation is COMPLETE for the requested sources and the existing checkout.** All five supplied roots were inventoried and reviewed; the 74 unique evidence files in the starter dataset were read fully, with all 213 planned chunks marked reviewed. The checkout copies match the supplied starter files after line-ending normalization. No requested source root or participant-evidence file was missing or unreadable. Fifty Git metadata entries remain excluded from semantic file reading because they are repository internals, not participant evidence. A final existence check found four absent paths among those excluded metadata entries; they are listed below.

Initial inventory was captured before content analysis. Counts exclude all newly generated preparation artifacts. Three supplied directory roots and two standalone files contributed 146 inventory entries and 21 directory nodes including the roots. The existing workspace contributed 160 entries. Combined initial inventory: **306 entries**. The final path check found 302 present; all 256 non-Git entries are present, while four absent entries are excluded Git metadata listed below.

| Source | Exact root | Inventory entries | Full content/visual review | Pending review | Excluded |
|---|---|---:|---:|---:|---:|
| S1 | `C:\Users\Razib\Downloads\ChatGPT-Hackathon Winning Strategy-20261024-2234-chatlogs-to-read.md` | 1 | 1 | 0 | 0 |
| S2 | `C:\Users\Razib\Downloads\Ghost_Data_Hackathon_Starter-by-chatgpt-work-mode` | 126 | 126 | 0 | 0 |
| S3 | `C:\Users\Razib\Downloads\ghost_data_starter_kit-chatgpt-chat-mode` | 16 | 16 | 0 | 0 |
| S4 | `C:\Users\Razib\Downloads\gemini-comprehensive-deepdive-and-all` | 2 | 2 | 0 | 0 |
| S5 | `D:\HR Orchastrate Hackathon 2026\hackathon-battle-plan.md` | 1 | 1 | 0 | 0 |
| S6 | `D:\Hackerrank Orchastrate Hackathon 2026` | 160 | 110 | 0 | 50 |

Totals: 226 text-file entries fully reviewed, 30 visual-file entries reviewed (15 distinct binary artifacts), zero pending entries, and 50 Git metadata entries excluded. All 256 non-Git entries received content or visual review. Newline-normalized content comparison yields 143 unique assets across those 256 entries; duplicate starter/check-out copies remain documented separately.

## Method, duplication and exclusions

- Enumerated complete source trees, including hidden files. Per-file absolute paths, format, bytes, SHA-256 and purpose are in [source-files.csv](research/source-files.csv); [inventory.json](research/inventory.json) also records normalized duplicate links. [Directory tree record](research/directory-trees.json).
- All strategy/code/preparation documents were read. Empty entrypoints/package markers were inspected as empty. Text clones were compared after newline normalization; binary duplicates use exact SHA-256. S2 older AGENTS typo differs from current official version.
- All nine CSVs were parsed for structure/counts. In addition, every participant-evidence CSV, SQL, log and JSON file has a full semantic review receipt in [the closed coverage report](research/review-completion/coverage-report.md); JSON contents were parsed and fully rendered with only whitespace omitted. These checks and analyst notes are distinct from solver accuracy or target prediction.
- Every distinct screenshot was visually inspected and every PDF page rendered/viewed; see [visual findings](research/VISUAL_REVIEW.md).
- Git metadata (50 files: packed objects/index/refs/config/logs/generated hooks) was inventoried by metadata/role and excluded from byte-by-byte semantic analysis. No generated hook was run.
- Four excluded S6 Git metadata paths were absent during the final path check: `.git\refs\codex\turn-diffs\captures\1792861712942\2f1c3af3-6b5b-4b6b-b47d-31afbb95649c\base` and `hackerrank-orchestrate-october26\.git\objects\pack\pack-bf5a3edbe451269c95603e07e4c2960f5df21280.{idx,pack,rev}`. Their role is repository metadata; no requested evidence or implementation file is missing. Per-entry presence is recorded in `research/inventory.json` and `research/source-files.csv`.
- No actual ZIP/tar/7z/RAR archives, Office documents, notebooks, dependency trees, caches or build artifacts existed in the five supplied source trees. Archive-looking filenames inside screenshots/JSON are business evidence, not local archive files. No extraction was needed.
- Research reading batches are historical review scratch, not automatic summaries or approved inference sources. The authoritative completion record is [review-progress.json](research/review-progress.json) with file-level receipts under `research/review-completion/`; it now records zero pending chunks.
- Code review covers correctness, types/API boundaries, I/O, dependencies, unsafe execution, edge cases, partial implementation, tests and integration; see [file analysis](research/FILE_ANALYSIS.md).

## External access

Official GitHub and all four Markdown snapshots verified. May/October landing pages and historical blog accessible. Help failed via web tool but was read through browser. Challenge portal failed web retrieval and redirected browser to login: live cutoff, upload slots and edition overrides unresolved. Do not inherit prior sessions' portal claims.

## Complete initial file listing

| Source | Relative path | Format | Bytes | Review state |
|---|---|---|---:|---|
| S1 | `ChatGPT-Hackathon Winning Strategy-20261024-2234-chatlogs-to-read.md` | .md | 47656 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\.gitignore` | extensionless | 98 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\agent_trace_instructions.md` | .md | 8163 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\AGENTS.md` | .md | 23548 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\CLAUDE.md` | .md | 11 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\code\evaluation\evaluation_report.md` | .md | 739 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\code\evaluation\main.py` | .py | 0 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\code\evaluation\usage_report.md` | .md | 1078 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\code\main.py` | .py | 0 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\code\tests\test_contract.py` | .py | 1828 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\code\tools\contract.py` | .py | 4975 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\code\tools\evaluate.py` | .py | 3144 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\code\tools\preflight.py` | .py | 2035 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\code\tools\validate_output.py` | .py | 926 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\deletion_requests.csv` | .csv | 163664 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\deletion_rules.csv` | .csv | 1039 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_accounts_failover_replica_20260902.sql` | .sql | 2052 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_failover_replica_20260920.sql` | .sql | 12250 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_inventory_20260213.sql` | .sql | 5436 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_inventory_20260310.sql` | .sql | 6545 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_inventory_20260404.sql` | .sql | 5721 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_inventory_20260504.sql` | .sql | 6084 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_inventory_20260524.sql` | .sql | 6601 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_inventory_20260618.sql` | .sql | 5787 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_inventory_20260703.sql` | .sql | 6626 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_inventory_20260723.sql` | .sql | 6994 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_inventory_20260817.sql` | .sql | 5922 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_inventory_20260905.sql` | .sql | 2314 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_inventory_20260916.sql` | .sql | 5550 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_read_replica_20260613.sql` | .sql | 19611 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_read_replica_20260708.sql` | .sql | 23547 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_read_replica_20260802.sql` | .sql | 19312 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_read_replica_20260827.sql` | .sql | 23576 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_read_replica_20260921.sql` | .sql | 24657 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_regional_replicas_20260330.sql` | .sql | 35506 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_regional_replicas_20260424.sql` | .sql | 36010 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_regional_replicas_20260519.sql` | .sql | 32168 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_reporting_replica_20260208.sql` | .sql | 19231 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_data_reporting_replica_20260305.sql` | .sql | 20275 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\databases\customer_search_primary_20260910.sql` | .sql | 826 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\documents\account_history_report_20260718.pdf` | .pdf | 65704 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\documents\delivery_correction_attachment.pdf` | .pdf | 66039 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\documents\legal_retention_register_20260529.pdf` | .pdf | 65857 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\documents\security_retention_extract.pdf` | .pdf | 64847 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\images\account_admin_console_20260926.png` | .png | 124989 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\images\analytics_profile_view_20260713.png` | .png | 129362 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\images\backup_restore_console_20260429.png` | .png | 155587 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\images\connector_management_console_20260807.png` | .png | 130271 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\images\customer_export_console_20260618.png` | .png | 134597 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\images\deleted_account_reference_20260310.png` | .png | 136696 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\images\marketing_profile_console.png` | .png | 129711 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\images\object_storage_browser_20260213.png` | .png | 154193 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\images\search_index_inspector_20260901.png` | .png | 121101 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\images\security_audit_explorer_20260905.png` | .png | 147699 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\images\support_ticket_console_20260524.png` | .png | 135008 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\application_trace_ap_northeast_20260730.log` | .log | 18839 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\application_trace_eu_north_20260302.log` | .log | 24885 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\cloud_runtime_export_af_south_20260930.log` | .log | 94518 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\cloud_runtime_export_us_west_20260608.log` | .log | 32266 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\notification_delivery_20260315.log` | .log | 8972 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\operations_stream_eu_central_20260705.log` | .log | 26198 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\operations_stream_me_central_20260203.log` | .log | 21199 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\resource_lookup_trace_20260218_083911.log` | .log | 10995 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\resource_lookup_trace_20260310_061801.log` | .log | 544 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\resource_lookup_trace_20260414_054007.log` | .log | 9836 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\resource_lookup_trace_20260509_104353.log` | .log | 13602 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\resource_lookup_trace_20260529_074313.log` | .log | 9626 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\resource_lookup_trace_20260623_053726.log` | .log | 12014 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\resource_lookup_trace_20260713_093359.log` | .log | 10662 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\resource_lookup_trace_20260728_054417.log` | .log | 9052 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\resource_lookup_trace_20260822_103910.log` | .log | 9059 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\resource_lookup_trace_20260911_074253.log` | .log | 12248 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\resource_lookup_trace_20260926_103856.log` | .log | 11743 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\search_index_diagnostic_20260906.log` | .log | 8013 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\service_events_ap_south_20260915.log` | .log | 22133 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\service_events_sa_east_20260516.log` | .log | 23481 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\structured_service_events_ca_central_20260419.log` | .log | 38660 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\structured_service_events_eu_west_20260918.log` | .log | 31199 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\support_replica.log` | .log | 1863 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\syslog_archive_ap_southeast_20260325.log` | .log | 25968 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\logs\syslog_archive_us_east_20260824.log` | .log | 26414 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\connector_configurations_20260812.json` | .json | 9788 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_account_handover_20261001.txt` | .txt | 4488 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_analytics_report_20260907.json` | .json | 1351 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_data_snapshot_bundle_20260131.json` | .json | 14811 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_data_snapshot_bundle_20260223.json` | .json | 24174 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_data_snapshot_bundle_20260322.json` | .json | 13241 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_data_snapshot_bundle_20260416.json` | .json | 13027 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_data_snapshot_bundle_20260511.json` | .json | 25174 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_data_snapshot_bundle_20260605.json` | .json | 13830 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_data_snapshot_bundle_20260630.json` | .json | 23629 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_data_snapshot_bundle_20260725.json` | .json | 15328 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_data_snapshot_bundle_20260819.json` | .json | 13064 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_data_snapshot_bundle_20260913.json` | .json | 12146 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_data_snapshot_bundle_20260915.json` | .json | 1843 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_data_snapshot_bundle_20260917.json` | .json | 17406 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_export_jobs_20260914.json` | .json | 817 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\customer_export_manifest_20260409.json` | .json | 11462 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\security_audit_ledger_20261001.json` | .json | 4985 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\service_resource_export_20260129_114459.json` | .json | 10387 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\service_resource_export_20260228_103637.json` | .json | 9383 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\service_resource_export_20260320_072349.json` | .json | 9000 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\service_resource_export_20260429_083222.json` | .json | 9691 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\service_resource_export_20260514_114454.json` | .json | 8733 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\service_resource_export_20260603_083457.json` | .json | 9475 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\service_resource_export_20260628_062556.json` | .json | 8742 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\service_resource_export_20260718_104335.json` | .json | 10775 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\service_resource_export_20260807_074104.json` | .json | 8346 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\service_resource_export_20260901_053316.json` | .json | 9390 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence\records\service_resource_export_20260915_114455.json` | .json | 11804 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\evidence_files.csv` | .csv | 11089 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\output.csv` | .csv | 35 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\sample_deletion_requests.csv` | .csv | 9010 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\sample_output.csv` | .csv | 38648 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\system_activity.csv` | .csv | 657360 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\user_audit_log.csv` | .csv | 36709 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\dataset\user_identities.csv` | .csv | 126411 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\log.txt` | .txt | 2795 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\preparation\EVIDENCE_READINESS.md` | .md | 9466 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\preparation\FIRST_PROMPT.md` | .md | 1854 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\preparation\REQUIREMENTS.md` | .md | 4581 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\preparation\SOURCE_SNAPSHOT.md` | .md | 622 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\preparation\SYNTHETIC_CASES.md` | .md | 2300 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\preparation\VERIFICATION.md` | .md | 1183 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\problem_statement.md` | .md | 9036 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\README.md` | .md | 8386 | FULL_CONTENT_REVIEW |
| S2 | `orchestrate-oct26\START_HERE.md` | .md | 8051 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\.gitignore` | extensionless | 77 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\code\__init__.py` | .py | 0 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\code\evaluation\evaluation_report.md` | .md | 1725 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\code\evaluation\usage_report.md` | .md | 1287 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\code\tests\__init__.py` | .py | 0 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\code\tests\test_validator.py` | .py | 3650 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\code\tools\__init__.py` | .py | 0 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\code\tools\evaluate_samples.py` | .py | 2973 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\code\tools\index_evidence.py` | .py | 5153 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\code\tools\inspect_dataset.py` | .py | 1820 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\code\tools\validate_output.py` | .py | 7274 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\ENGINEERING_PLAN.md` | .md | 4315 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\install_starter.ps1` | .ps1 | 1764 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\PROMPT_FOR_CODEX.md` | .md | 4000 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\requirements.txt` | .txt | 30 | FULL_CONTENT_REVIEW |
| S3 | `ghost_data_starter\START_HERE.md` | .md | 3855 | FULL_CONTENT_REVIEW |
| S4 | `ghost_data_audit_agent.py` | .py | 45396 | FULL_CONTENT_REVIEW |
| S4 | `HackerRank Orchestrate Competition Strategy.md` | .md | 80672 | FULL_CONTENT_REVIEW |
| S5 | `hackathon-battle-plan.md` | .md | 15761 | FULL_CONTENT_REVIEW |
| S6 | `.git\config` | extensionless | 312 | EXCLUDED_GIT_METADATA |
| S6 | `.git\description` | extensionless | 73 | EXCLUDED_GIT_METADATA |
| S6 | `.git\FETCH_HEAD` | extensionless | 0 | EXCLUDED_GIT_METADATA |
| S6 | `.git\HEAD` | extensionless | 21 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\applypatch-msg.sample` | .sample | 478 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\commit-msg.sample` | .sample | 896 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\fsmonitor-watchman.sample` | .sample | 4726 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\post-update.sample` | .sample | 189 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\pre-applypatch.sample` | .sample | 424 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\pre-commit.sample` | .sample | 1649 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\pre-merge-commit.sample` | .sample | 416 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\pre-push.sample` | .sample | 1374 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\pre-rebase.sample` | .sample | 4898 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\pre-receive.sample` | .sample | 544 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\prepare-commit-msg.sample` | .sample | 1492 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\push-to-checkout.sample` | .sample | 2783 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\sendemail-validate.sample` | .sample | 2308 | EXCLUDED_GIT_METADATA |
| S6 | `.git\hooks\update.sample` | .sample | 3650 | EXCLUDED_GIT_METADATA |
| S6 | `.git\info\exclude` | extensionless | 240 | EXCLUDED_GIT_METADATA |
| S6 | `.git\objects\d7\5a9edf438314e7afb8b3661504b76bbf111b8b` | extensionless | 75 | EXCLUDED_GIT_METADATA |
| S6 | `.git\refs\codex\turn-diffs\captures\1792861712942\2f1c3af3-6b5b-4b6b-b47d-31afbb95649c\base` | extensionless | 41 | EXCLUDED_GIT_METADATA |
| S6 | `.git\refs\codex\turn-diffs\checkpoints\0fc363d4dc7c61712b9b67f1346d245d\063ec901041a39ed8393336726195173\1792861680695\624c228c-02c6-4b66-8ef8-fdfe6bec115d` | extensionless | 41 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\config` | extensionless | 330 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\description` | extensionless | 73 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\HEAD` | extensionless | 21 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\applypatch-msg.sample` | .sample | 478 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\commit-msg.sample` | .sample | 896 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\fsmonitor-watchman.sample` | .sample | 4726 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\post-update.sample` | .sample | 189 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\pre-applypatch.sample` | .sample | 424 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\pre-commit.sample` | .sample | 1649 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\pre-merge-commit.sample` | .sample | 416 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\pre-push.sample` | .sample | 1374 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\pre-rebase.sample` | .sample | 4898 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\pre-receive.sample` | .sample | 544 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\prepare-commit-msg.sample` | .sample | 1492 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\push-to-checkout.sample` | .sample | 2783 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\sendemail-validate.sample` | .sample | 2308 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\hooks\update.sample` | .sample | 3650 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\index` | extensionless | 14059 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\info\exclude` | extensionless | 240 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\logs\HEAD` | extensionless | 215 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\logs\refs\heads\main` | extensionless | 215 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\logs\refs\remotes\origin\HEAD` | extensionless | 215 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\objects\pack\pack-bf5a3edbe451269c95603e07e4c2960f5df21280.idx` | .idx | 10732 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\objects\pack\pack-bf5a3edbe451269c95603e07e4c2960f5df21280.pack` | .pack | 1991822 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\objects\pack\pack-bf5a3edbe451269c95603e07e4c2960f5df21280.rev` | .rev | 1432 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\packed-refs` | extensionless | 357 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\refs\heads\main` | extensionless | 41 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\.git\refs\remotes\origin\HEAD` | extensionless | 30 | EXCLUDED_GIT_METADATA |
| S6 | `hackerrank-orchestrate-october26\agent_trace_instructions.md` | .md | 8293 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\AGENTS.md` | .md | 23969 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\CLAUDE.md` | .md | 12 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\code\evaluation\main.py` | .py | 0 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\code\main.py` | .py | 0 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\deletion_requests.csv` | .csv | 164183 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\deletion_rules.csv` | .csv | 1055 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_accounts_failover_replica_20260902.sql` | .sql | 2077 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_failover_replica_20260920.sql` | .sql | 12304 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_inventory_20260213.sql` | .sql | 5478 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_inventory_20260310.sql` | .sql | 6594 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_inventory_20260404.sql` | .sql | 5765 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_inventory_20260504.sql` | .sql | 6130 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_inventory_20260524.sql` | .sql | 6651 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_inventory_20260618.sql` | .sql | 5831 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_inventory_20260703.sql` | .sql | 6676 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_inventory_20260723.sql` | .sql | 7046 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_inventory_20260817.sql` | .sql | 5967 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_inventory_20260905.sql` | .sql | 2333 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_inventory_20260916.sql` | .sql | 5593 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_read_replica_20260613.sql` | .sql | 19683 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_read_replica_20260708.sql` | .sql | 23632 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_read_replica_20260802.sql` | .sql | 19383 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_read_replica_20260827.sql` | .sql | 23657 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_read_replica_20260921.sql` | .sql | 24740 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_regional_replicas_20260330.sql` | .sql | 35620 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_regional_replicas_20260424.sql` | .sql | 36128 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_regional_replicas_20260519.sql` | .sql | 32282 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_reporting_replica_20260208.sql` | .sql | 19302 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_data_reporting_replica_20260305.sql` | .sql | 20348 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\databases\customer_search_primary_20260910.sql` | .sql | 838 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\documents\account_history_report_20260718.pdf` | .pdf | 65704 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\documents\delivery_correction_attachment.pdf` | .pdf | 66039 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\documents\legal_retention_register_20260529.pdf` | .pdf | 65857 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\documents\security_retention_extract.pdf` | .pdf | 64847 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\images\account_admin_console_20260926.png` | .png | 124989 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\images\analytics_profile_view_20260713.png` | .png | 129362 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\images\backup_restore_console_20260429.png` | .png | 155587 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\images\connector_management_console_20260807.png` | .png | 130271 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\images\customer_export_console_20260618.png` | .png | 134597 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\images\deleted_account_reference_20260310.png` | .png | 136696 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\images\marketing_profile_console.png` | .png | 129711 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\images\object_storage_browser_20260213.png` | .png | 154193 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\images\search_index_inspector_20260901.png` | .png | 121101 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\images\security_audit_explorer_20260905.png` | .png | 147699 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\images\support_ticket_console_20260524.png` | .png | 135008 | FULL_VISUAL_AND_EXTRACTION_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\application_trace_ap_northeast_20260730.log` | .log | 18932 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\application_trace_eu_north_20260302.log` | .log | 25010 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\cloud_runtime_export_af_south_20260930.log` | .log | 94823 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\cloud_runtime_export_us_west_20260608.log` | .log | 32394 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\notification_delivery_20260315.log` | .log | 9011 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\operations_stream_eu_central_20260705.log` | .log | 26326 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\operations_stream_me_central_20260203.log` | .log | 21302 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\resource_lookup_trace_20260218_083911.log` | .log | 11049 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\resource_lookup_trace_20260310_061801.log` | .log | 548 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\resource_lookup_trace_20260414_054007.log` | .log | 9886 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\resource_lookup_trace_20260509_104353.log` | .log | 13670 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\resource_lookup_trace_20260529_074313.log` | .log | 9674 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\resource_lookup_trace_20260623_053726.log` | .log | 12074 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\resource_lookup_trace_20260713_093359.log` | .log | 10716 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\resource_lookup_trace_20260728_054417.log` | .log | 9098 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\resource_lookup_trace_20260822_103910.log` | .log | 9105 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\resource_lookup_trace_20260911_074253.log` | .log | 12310 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\resource_lookup_trace_20260926_103856.log` | .log | 11801 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\search_index_diagnostic_20260906.log` | .log | 8049 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\service_events_ap_south_20260915.log` | .log | 22237 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\service_events_sa_east_20260516.log` | .log | 23591 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\structured_service_events_ca_central_20260419.log` | .log | 38796 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\structured_service_events_eu_west_20260918.log` | .log | 31311 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\support_replica.log` | .log | 1873 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\syslog_archive_ap_southeast_20260325.log` | .log | 26082 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\logs\syslog_archive_us_east_20260824.log` | .log | 26532 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\connector_configurations_20260812.json` | .json | 10107 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_account_handover_20261001.txt` | .txt | 4534 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_analytics_report_20260907.json` | .json | 1404 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_data_snapshot_bundle_20260131.json` | .json | 15256 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_data_snapshot_bundle_20260223.json` | .json | 24885 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_data_snapshot_bundle_20260322.json` | .json | 13647 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_data_snapshot_bundle_20260416.json` | .json | 13423 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_data_snapshot_bundle_20260511.json` | .json | 25927 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_data_snapshot_bundle_20260605.json` | .json | 14243 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_data_snapshot_bundle_20260630.json` | .json | 24337 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_data_snapshot_bundle_20260725.json` | .json | 15789 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_data_snapshot_bundle_20260819.json` | .json | 13456 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_data_snapshot_bundle_20260913.json` | .json | 12514 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_data_snapshot_bundle_20260915.json` | .json | 1901 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_data_snapshot_bundle_20260917.json` | .json | 17941 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_export_jobs_20260914.json` | .json | 848 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\customer_export_manifest_20260409.json` | .json | 11837 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\security_audit_ledger_20261001.json` | .json | 5152 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\service_resource_export_20260129_114459.json` | .json | 10720 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\service_resource_export_20260228_103637.json` | .json | 9689 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\service_resource_export_20260320_072349.json` | .json | 9296 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\service_resource_export_20260429_083222.json` | .json | 10005 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\service_resource_export_20260514_114454.json` | .json | 9017 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\service_resource_export_20260603_083457.json` | .json | 9775 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\service_resource_export_20260628_062556.json` | .json | 9028 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\service_resource_export_20260718_104335.json` | .json | 11127 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\service_resource_export_20260807_074104.json` | .json | 8619 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\service_resource_export_20260901_053316.json` | .json | 9695 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence\records\service_resource_export_20260915_114455.json` | .json | 12177 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\evidence_files.csv` | .csv | 11184 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\output.csv` | .csv | 36 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\sample_deletion_requests.csv` | .csv | 9043 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\sample_output.csv` | .csv | 38681 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\system_activity.csv` | .csv | 661372 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\user_audit_log.csv` | .csv | 37016 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\dataset\user_identities.csv` | .csv | 127262 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\problem_statement.md` | .md | 9198 | FULL_CONTENT_REVIEW |
| S6 | `hackerrank-orchestrate-october26\README.md` | .md | 8543 | FULL_CONTENT_REVIEW |
