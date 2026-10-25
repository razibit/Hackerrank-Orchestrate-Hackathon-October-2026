# Evidence format readiness

These are structural extraction checks on all 94 manifest files, not audit conclusions or predictions.

| File | Format | Structural check |
|---|---|---|
| service_events_ap_south_20260915.log | .log | UTF-8 decoded; 104 lines |
| customer_data_snapshot_bundle_20260917.json | .json | JSON parsed; keys: exported_at, source, snapshots |
| customer_account_handover_20261001.txt | .txt | UTF-8 decoded; 46 lines |
| account_admin_console_20260926.png | .png | Image decoded: 1800 × 1200; OCR/vision extraction still to implement |
| customer_data_read_replica_20260921.sql | .sql | SQLite loaded in isolated memory; 2 tables |
| structured_service_events_eu_west_20260918.log | .log | UTF-8 decoded; 112 lines |
| customer_data_snapshot_bundle_20260913.json | .json | JSON parsed; keys: exported_at, source, snapshots |
| search_index_diagnostic_20260906.log | .log | UTF-8 decoded; 36 lines |
| search_index_inspector_20260901.png | .png | Image decoded: 1800 × 1100; OCR/vision extraction still to implement |
| customer_data_read_replica_20260827.sql | .sql | SQLite loaded in isolated memory; 2 tables |
| syslog_archive_us_east_20260824.log | .log | UTF-8 decoded; 118 lines |
| customer_data_snapshot_bundle_20260819.json | .json | JSON parsed; keys: exported_at, source, snapshots |
| connector_configurations_20260812.json | .json | JSON parsed; keys: exported_at, origin, record_count, records |
| connector_management_console_20260807.png | .png | Image decoded: 1800 × 1150; OCR/vision extraction still to implement |
| customer_data_read_replica_20260802.sql | .sql | SQLite loaded in isolated memory; 2 tables |
| application_trace_ap_northeast_20260730.log | .log | UTF-8 decoded; 93 lines |
| customer_data_snapshot_bundle_20260725.json | .json | JSON parsed; keys: exported_at, source, snapshots |
| account_history_report_20260718.pdf | .pdf | 2 pages; 718 extracted text characters |
| analytics_profile_view_20260713.png | .png | Image decoded: 1800 × 1150; OCR/vision extraction still to implement |
| customer_data_read_replica_20260708.sql | .sql | SQLite loaded in isolated memory; 2 tables |
| operations_stream_eu_central_20260705.log | .log | UTF-8 decoded; 128 lines |
| customer_data_snapshot_bundle_20260630.json | .json | JSON parsed; keys: exported_at, source, snapshots |
| customer_export_console_20260618.png | .png | Image decoded: 1800 × 1100; OCR/vision extraction still to implement |
| customer_data_read_replica_20260613.sql | .sql | SQLite loaded in isolated memory; 2 tables |
| cloud_runtime_export_us_west_20260608.log | .log | UTF-8 decoded; 128 lines |
| customer_data_snapshot_bundle_20260605.json | .json | JSON parsed; keys: exported_at, source, snapshots |
| legal_retention_register_20260529.pdf | .pdf | 2 pages; 1002 extracted text characters |
| support_ticket_console_20260524.png | .png | Image decoded: 1800 × 1200; OCR/vision extraction still to implement |
| customer_data_regional_replicas_20260519.sql | .sql | SQLite loaded in isolated memory; 3 tables |
| service_events_sa_east_20260516.log | .log | UTF-8 decoded; 110 lines |
| customer_data_snapshot_bundle_20260511.json | .json | JSON parsed; keys: exported_at, source, snapshots |
| backup_restore_console_20260429.png | .png | Image decoded: 1800 × 1150; OCR/vision extraction still to implement |
| customer_data_regional_replicas_20260424.sql | .sql | SQLite loaded in isolated memory; 3 tables |
| structured_service_events_ca_central_20260419.log | .log | UTF-8 decoded; 136 lines |
| customer_data_snapshot_bundle_20260416.json | .json | JSON parsed; keys: exported_at, source, snapshots |
| customer_export_manifest_20260409.json | .json | JSON parsed; keys: exported_at, origin, record_count, records |
| security_audit_explorer_20260905.png | .png | Image decoded: 1800 × 1100; OCR/vision extraction still to implement |
| customer_data_regional_replicas_20260330.sql | .sql | SQLite loaded in isolated memory; 3 tables |
| syslog_archive_ap_southeast_20260325.log | .log | UTF-8 decoded; 114 lines |
| customer_data_snapshot_bundle_20260322.json | .json | JSON parsed; keys: exported_at, source, snapshots |
| notification_delivery_20260315.log | .log | UTF-8 decoded; 39 lines |
| deleted_account_reference_20260310.png | .png | Image decoded: 1800 × 1100; OCR/vision extraction still to implement |
| customer_data_reporting_replica_20260305.sql | .sql | SQLite loaded in isolated memory; 2 tables |
| application_trace_eu_north_20260302.log | .log | UTF-8 decoded; 125 lines |
| customer_data_snapshot_bundle_20260223.json | .json | JSON parsed; keys: exported_at, source, snapshots |
| object_storage_browser_20260213.png | .png | Image decoded: 1800 × 1150; OCR/vision extraction still to implement |
| customer_data_reporting_replica_20260208.sql | .sql | SQLite loaded in isolated memory; 2 tables |
| operations_stream_me_central_20260203.log | .log | UTF-8 decoded; 103 lines |
| customer_data_snapshot_bundle_20260131.json | .json | JSON parsed; keys: exported_at, source, snapshots |
| security_audit_ledger_20261001.json | .json | JSON parsed; keys: exported_at, origin, record_count, records |
| customer_data_snapshot_bundle_20260915.json | .json | JSON parsed; keys: exported_at, source, snapshots |
| customer_data_failover_replica_20260920.sql | .sql | SQLite loaded in isolated memory; 2 tables |
| cloud_runtime_export_af_south_20260930.log | .log | UTF-8 decoded; 305 lines |
| customer_accounts_failover_replica_20260902.sql | .sql | SQLite loaded in isolated memory; 2 tables |
| security_retention_extract.pdf | .pdf | 1 pages; 616 extracted text characters |
| customer_analytics_report_20260907.json | .json | JSON parsed; keys: captured_at, source, collection, records |
| customer_search_primary_20260910.sql | .sql | SQLite loaded in isolated memory; 1 tables |
| delivery_correction_attachment.pdf | .pdf | 2 pages; 837 extracted text characters |
| customer_export_jobs_20260914.json | .json | JSON parsed; keys: captured_at, source, collection, records |
| marketing_profile_console.png | .png | Image decoded: 1500 × 920; OCR/vision extraction still to implement |
| support_replica.log | .log | UTF-8 decoded; 10 lines |
| service_resource_export_20260129_114459.json | .json | JSON parsed; keys: exported_at, region, service_exports, source |
| customer_data_inventory_20260213.sql | .sql | SQLite loaded in isolated memory; 9 tables |
| resource_lookup_trace_20260218_083911.log | .log | UTF-8 decoded; 54 lines |
| service_resource_export_20260228_103637.json | .json | JSON parsed; keys: exported_at, region, service_exports, source |
| customer_data_inventory_20260310.sql | .sql | SQLite loaded in isolated memory; 9 tables |
| resource_lookup_trace_20260310_061801.log | .log | UTF-8 decoded; 4 lines |
| service_resource_export_20260320_072349.json | .json | JSON parsed; keys: exported_at, region, service_exports, source |
| customer_data_inventory_20260404.sql | .sql | SQLite loaded in isolated memory; 9 tables |
| resource_lookup_trace_20260414_054007.log | .log | UTF-8 decoded; 50 lines |
| service_resource_export_20260429_083222.json | .json | JSON parsed; keys: exported_at, region, service_exports, source |
| customer_data_inventory_20260504.sql | .sql | SQLite loaded in isolated memory; 9 tables |
| resource_lookup_trace_20260509_104353.log | .log | UTF-8 decoded; 68 lines |
| service_resource_export_20260514_114454.json | .json | JSON parsed; keys: exported_at, region, service_exports, source |
| customer_data_inventory_20260524.sql | .sql | SQLite loaded in isolated memory; 9 tables |
| resource_lookup_trace_20260529_074313.log | .log | UTF-8 decoded; 48 lines |
| service_resource_export_20260603_083457.json | .json | JSON parsed; keys: exported_at, region, service_exports, source |
| customer_data_inventory_20260618.sql | .sql | SQLite loaded in isolated memory; 9 tables |
| resource_lookup_trace_20260623_053726.log | .log | UTF-8 decoded; 60 lines |
| service_resource_export_20260628_062556.json | .json | JSON parsed; keys: exported_at, region, service_exports, source |
| customer_data_inventory_20260703.sql | .sql | SQLite loaded in isolated memory; 9 tables |
| resource_lookup_trace_20260713_093359.log | .log | UTF-8 decoded; 54 lines |
| service_resource_export_20260718_104335.json | .json | JSON parsed; keys: exported_at, region, service_exports, source |
| customer_data_inventory_20260723.sql | .sql | SQLite loaded in isolated memory; 9 tables |
| resource_lookup_trace_20260728_054417.log | .log | UTF-8 decoded; 46 lines |
| service_resource_export_20260807_074104.json | .json | JSON parsed; keys: exported_at, region, service_exports, source |
| customer_data_inventory_20260817.sql | .sql | SQLite loaded in isolated memory; 9 tables |
| resource_lookup_trace_20260822_103910.log | .log | UTF-8 decoded; 46 lines |
| service_resource_export_20260901_053316.json | .json | JSON parsed; keys: exported_at, region, service_exports, source |
| customer_data_inventory_20260905.sql | .sql | SQLite loaded in isolated memory; 9 tables |
| resource_lookup_trace_20260911_074253.log | .log | UTF-8 decoded; 62 lines |
| service_resource_export_20260915_114455.json | .json | JSON parsed; keys: exported_at, region, service_exports, source |
| customer_data_inventory_20260916.sql | .sql | SQLite loaded in isolated memory; 9 tables |
| resource_lookup_trace_20260926_103856.log | .log | UTF-8 decoded; 58 lines |
