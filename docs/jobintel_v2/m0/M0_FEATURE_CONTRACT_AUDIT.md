# M0 Feature Contract Audit

Evidence: source/metadata inspection and a passing contract test subset (`tests/test_cloud_contracts.py`). No model was retrained or serialized artifact loaded by this feature-list extraction.

## Count verification

| Market | Raw/request contract | Post-transform/model input | Composition | Status |
|---|---:|---:|---|---|
| India | 290 | 327 | 6 scalar/raw metadata fields + 284 binary skill indicators; fitted preprocessing expands categorical fields to 327 columns | Verified |
| USA | 123 | 123 | 41 transformed metadata features + 82 binary skill indicators | Verified |

The historical 290 India / 123 USA claims are confirmed only when the representation is named. India inference receives an ordered 290-column raw DataFrame, then `india_preprocessor.transform` yields the transformed contract recorded as 327 columns. USA builds processed metadata and appends 82 ordered skills for 123 model inputs. They are not analogous raw contracts and must not be merged by count alone.

## India raw ordered feature sequence

Authoritative checked-in order: `models/india/final_feature_list.json` → `feature_names_raw`. The complete sequence follows; `skill_*` names are categorical binary indicators.

```text
normalized_role
experience_midpoint_years
experience_range_years
city_grouped
work_mode
total_selected_skill_count
skill__net
skill_3d
skill_3d_modeling
skill_abap
skill_administration
skill_advanced_excel
skill_agile
skill_ai
skill_aiml
skill_airflow
skill_analysis
skill_analytics
skill_android
skill_android_application_development
skill_angular
skill_api
skill_api_integration
skill_api_testing
skill_application
skill_application_development
skill_architectural_design
skill_architecture
skill_asp_net_core
skill_auto
skill_autocad
skill_autocad_2d
skill_automation
skill_automation_testing
skill_automotive
skill_aws
skill_aws_cloud
skill_azure
skill_azure_cloud
skill_azure_data_factory
skill_azure_databricks
skill_azure_devops
skill_b2b_sales
skill_backend
skill_bi
skill_big_data
skill_big_data_engineer
skill_bigquery
skill_boot
skill_bootstrap
skill_boq_preparation
skill_breakdown_maintenance
skill_business_analysis
skill_business_development
skill_c
skill_c_
skill_c__
skill_ccna
skill_cd
skill_certified
skill_ci_cd_pipeline
skill_ci_cd
skill_cloud
skill_coding
skill_communication_skills
skill_configuration
skill_consulting
skill_control
skill_core
skill_core_banking
skill_cost_estimation
skill_css
skill_customer_support
skill_data
skill_data_analysis
skill_data_architecture
skill_data_bricks
skill_data_engineering
skill_data_modeling
skill_data_science
skill_data_warehousing
skill_database
skill_dbms
skill_deep_learning
skill_design
skill_design_engineering
skill_design_patterns
skill_desktop
skill_desktop_support
skill_development
skill_devops
skill_devops_tools
skill_django
skill_docker
skill_documentation
skill_dot
skill_drawing
skill_electrical_maintenance
skill_electronics
skill_embedded_systems
skill_encryption
skill_end
skill_engineering
skill_english
skill_er_studio
skill_erp
skill_erwin
skill_estimation
skill_etl
skill_excel
skill_express
skill_fabrication
skill_fast_api
skill_fico
skill_field_service
skill_flask
skill_flutter
skill_framework
skill_front_end
skill_frontend_development
skill_full_stack
skill_fullstack_development
skill_gcp
skill_gcp_cloud
skill_generative_ai
skill_git
skill_github
skill_golang
skill_good_english_communication
skill_graphql
skill_hadoop
skill_hardware
skill_hcc_coding
skill_heavy_fabrication
skill_hibernate
skill_hindi
skill_hiring
skill_hive
skill_html
skill_hydraulics
skill_iatf
skill_implementation
skill_industrial_automation
skill_industrial_sales
skill_installation
skill_integration
skill_international_technical_support
skill_iso
skill_it_helpdesk
skill_itsm
skill_java
skill_java_development
skill_java_fullstack
skill_javascript
skill_jenkins
skill_jira
skill_jquery
skill_json
skill_kafka
skill_kotlin
skill_kubernetes
skill_l1_support
skill_laravel
skill_linux
skill_llm
skill_machine
skill_machine_learning
skill_machining
skill_maintenance
skill_maintenance_engineering
skill_management
skill_manual
skill_manual_testing
skill_maven
skill_medical
skill_medical_coding
skill_microservices
skill_mm
skill_mobile_application_development
skill_mongodb
skill_mvc
skill_mysql
skill_net
skill_net_core
skill_network_engineering
skill_network_support
skill_networking
skill_nlp
skill_node_js
skill_nosql
skill_npd
skill_office
skill_oops
skill_operations
skill_oracle
skill_os_installation
skill_outlook_configuration
skill_pandas
skill_php
skill_pl_sql
skill_planning
skill_plc
skill_postgresql
skill_power_bi
skill_powershell
skill_problem_solving
skill_process
skill_procurement
skill_product_management
skill_production
skill_program
skill_programming
skill_project
skill_project_management
skill_python
skill_python_development
skill_pytorch
skill_qa
skill_qms
skill_quality
skill_quality_assurance
skill_quality_audit
skill_quality_control
skill_quality_engineering
skill_react
skill_react_native
skill_reacts_js
skill_redux
skill_reporting
skill_rest_api
skill_restfull_api
skill_revit
skill_s4_hana
skill_sales
skill_sales_engineering
skill_salesforce
skill_sap
skill_sap_abap
skill_sap_fico
skill_sap_hana
skill_sap_mm
skill_sap_s_hana
skill_sap_sd
skill_sap_testing
skill_saps
skill_scala
skill_scripting
skill_selenium
skill_senior
skill_service_desk
skill_service_engineering
skill_servicenow
skill_servicenow_development
skill_servicing
skill_sheet_metal
skill_shell_scripting
skill_sketchup
skill_snowflake
skill_software
skill_software_development
skill_software_testing
skill_solid_works
skill_spark
skill_spring
skill_spring_boot
skill_sql
skill_sql_queries
skill_sql_server
skill_sr
skill_stack
skill_sub_contractor_billing
skill_system
skill_tableau
skill_technical
skill_technical_sales
skill_technical_support
skill_technical_voice_process
skill_tensorflow
skill_terraform
skill_test
skill_tools
skill_troubleshooting
skill_typescript
skill_ui_ux
skill_vmc
skill_voice_process
skill_web_api
skill_web_technologies
skill_welding
skill_wordpress
```

## India transformed ordered feature sequence

Authoritative checked-in order: `models/india/final_feature_list.json` → `feature_names_transformed`. This is the model-facing postprocessor sequence.

```text
normalized_role_AI / ML Engineer
normalized_role_Business Analyst
normalized_role_Cloud / DevOps
normalized_role_Cybersecurity
normalized_role_Data Analyst
normalized_role_Data Engineer
normalized_role_Data Scientist
normalized_role_Database Administrator
normalized_role_Frontend Developer
normalized_role_Full Stack Developer
normalized_role_Other Technology
normalized_role_Product / Program Manager
normalized_role_QA / Testing
normalized_role_Software Engineer
city_grouped_Ahmedabad
city_grouped_Aurangabad
city_grouped_Bengaluru
city_grouped_Chandigarh
city_grouped_Chennai
city_grouped_Coimbatore
city_grouped_Delhi NCR
city_grouped_Faridabad
city_grouped_Gurugram
city_grouped_Hyderabad
city_grouped_Jaipur
city_grouped_Kochi
city_grouped_Kolkata
city_grouped_Mohali
city_grouped_Mumbai
city_grouped_Nagpur
city_grouped_Nashik
city_grouped_Noida
city_grouped_Other
city_grouped_Pune
city_grouped_Remote
city_grouped_Surat
city_grouped_Vadodara
work_mode_Hybrid
work_mode_Onsite
work_mode_Remote
experience_midpoint_years
experience_range_years
total_selected_skill_count
skill__net
skill_3d
skill_3d_modeling
skill_abap
skill_administration
skill_advanced_excel
skill_agile
skill_ai
skill_aiml
skill_airflow
skill_analysis
skill_analytics
skill_android
skill_android_application_development
skill_angular
skill_api
skill_api_integration
skill_api_testing
skill_application
skill_application_development
skill_architectural_design
skill_architecture
skill_asp_net_core
skill_auto
skill_autocad
skill_autocad_2d
skill_automation
skill_automation_testing
skill_automotive
skill_aws
skill_aws_cloud
skill_azure
skill_azure_cloud
skill_azure_data_factory
skill_azure_databricks
skill_azure_devops
skill_b2b_sales
skill_backend
skill_bi
skill_big_data
skill_big_data_engineer
skill_bigquery
skill_boot
skill_bootstrap
skill_boq_preparation
skill_breakdown_maintenance
skill_business_analysis
skill_business_development
skill_c
skill_c_
skill_c__
skill_ccna
skill_cd
skill_certified
skill_ci_cd_pipeline
skill_ci_cd
skill_cloud
skill_coding
skill_communication_skills
skill_configuration
skill_consulting
skill_control
skill_core
skill_core_banking
skill_cost_estimation
skill_css
skill_customer_support
skill_data
skill_data_analysis
skill_data_architecture
skill_data_bricks
skill_data_engineering
skill_data_modeling
skill_data_science
skill_data_warehousing
skill_database
skill_dbms
skill_deep_learning
skill_design
skill_design_engineering
skill_design_patterns
skill_desktop
skill_desktop_support
skill_development
skill_devops
skill_devops_tools
skill_django
skill_docker
skill_documentation
skill_dot
skill_drawing
skill_electrical_maintenance
skill_electronics
skill_embedded_systems
skill_encryption
skill_end
skill_engineering
skill_english
skill_er_studio
skill_erp
skill_erwin
skill_estimation
skill_etl
skill_excel
skill_express
skill_fabrication
skill_fast_api
skill_fico
skill_field_service
skill_flask
skill_flutter
skill_framework
skill_front_end
skill_frontend_development
skill_full_stack
skill_fullstack_development
skill_gcp
skill_gcp_cloud
skill_generative_ai
skill_git
skill_github
skill_golang
skill_good_english_communication
skill_graphql
skill_hadoop
skill_hardware
skill_hcc_coding
skill_heavy_fabrication
skill_hibernate
skill_hindi
skill_hiring
skill_hive
skill_html
skill_hydraulics
skill_iatf
skill_implementation
skill_industrial_automation
skill_industrial_sales
skill_installation
skill_integration
skill_international_technical_support
skill_iso
skill_it_helpdesk
skill_itsm
skill_java
skill_java_development
skill_java_fullstack
skill_javascript
skill_jenkins
skill_jira
skill_jquery
skill_json
skill_kafka
skill_kotlin
skill_kubernetes
skill_l1_support
skill_laravel
skill_linux
skill_llm
skill_machine
skill_machine_learning
skill_machining
skill_maintenance
skill_maintenance_engineering
skill_management
skill_manual
skill_manual_testing
skill_maven
skill_medical
skill_medical_coding
skill_microservices
skill_mm
skill_mobile_application_development
skill_mongodb
skill_mvc
skill_mysql
skill_net
skill_net_core
skill_network_engineering
skill_network_support
skill_networking
skill_nlp
skill_node_js
skill_nosql
skill_npd
skill_office
skill_oops
skill_operations
skill_oracle
skill_os_installation
skill_outlook_configuration
skill_pandas
skill_php
skill_pl_sql
skill_planning
skill_plc
skill_postgresql
skill_power_bi
skill_powershell
skill_problem_solving
skill_process
skill_procurement
skill_product_management
skill_production
skill_program
skill_programming
skill_project
skill_project_management
skill_python
skill_python_development
skill_pytorch
skill_qa
skill_qms
skill_quality
skill_quality_assurance
skill_quality_audit
skill_quality_control
skill_quality_engineering
skill_react
skill_react_native
skill_reacts_js
skill_redux
skill_reporting
skill_rest_api
skill_restfull_api
skill_revit
skill_s4_hana
skill_sales
skill_sales_engineering
skill_salesforce
skill_sap
skill_sap_abap
skill_sap_fico
skill_sap_hana
skill_sap_mm
skill_sap_s_hana
skill_sap_sd
skill_sap_testing
skill_saps
skill_scala
skill_scripting
skill_selenium
skill_senior
skill_service_desk
skill_service_engineering
skill_servicenow
skill_servicenow_development
skill_servicing
skill_sheet_metal
skill_shell_scripting
skill_sketchup
skill_snowflake
skill_software
skill_software_development
skill_software_testing
skill_solid_works
skill_spark
skill_spring
skill_spring_boot
skill_sql
skill_sql_queries
skill_sql_server
skill_sr
skill_stack
skill_sub_contractor_billing
skill_system
skill_tableau
skill_technical
skill_technical_sales
skill_technical_support
skill_technical_voice_process
skill_tensorflow
skill_terraform
skill_test
skill_tools
skill_troubleshooting
skill_typescript
skill_ui_ux
skill_vmc
skill_voice_process
skill_web_api
skill_web_technologies
skill_welding
skill_wordpress
```

## USA model ordered feature sequence

Authoritative checked-in order: `models/phase5/feature_metadata.json` → `feature_names`. `metadata_cols` is the input order to `MetadataTransformer`; it one-hot encodes `seniority`, `role_family`, `city_clean`, then appends `is_remote`, `num_skills`. The 82 `tech_skills` indicators are appended in metadata order.

```text
seniority_Intern
seniority_Junior / Entry
seniority_Lead / Principal / Executive
seniority_Mid / Unspecified
seniority_Senior
role_family_Backend Developer
role_family_Data / BI Analyst
role_family_Data Engineer
role_family_Data Scientist
role_family_DevOps / Cloud / Platform
role_family_Embedded & Hardware
role_family_Engineering Management
role_family_Frontend Developer
role_family_Full-Stack Developer
role_family_ML / AI Engineer
role_family_Mobile Engineer
role_family_Other Tech
role_family_QA / SDET
role_family_Security Engineer
role_family_Software Engineer
role_family_Solutions & Architecture
role_family_Systems & Network Engineer
role_family_Technical Product & PM
city_clean_Boston
city_clean_Chicago
city_clean_Costa Mesa
city_clean_Denver
city_clean_Hawthorne
city_clean_Long Beach
city_clean_Los Angeles
city_clean_Mountain View
city_clean_New York
city_clean_New York City
city_clean_Other
city_clean_San Francisco
city_clean_San Jose
city_clean_Seattle
city_clean_Toronto
city_clean_Washington
is_remote
num_skills
skill_airflow
skill_android
skill_angular
skill_ansible
skill_aws
skill_azure
skill_bigquery
skill_blockchain
skill_c#
skill_c++
skill_ci_cd
skill_computer_vision
skill_data_engineering
skill_data_science
skill_databricks
skill_dbt
skill_deep_learning
skill_devops
skill_django
skill_docker
skill_elasticsearch
skill_embedded
skill_etl
skill_fastapi
skill_flask
skill_flutter
skill_gcp
skill_gis
skill_git
skill_go
skill_graphql
skill_grpc
skill_hadoop
skill_hardware
skill_html_css
skill_ios
skill_java
skill_javascript
skill_kafka
skill_kotlin
skill_kubernetes
skill_linux
skill_llm
skill_looker
skill_machine_learning
skill_microservices
skill_next_js
skill_nlp
skill_node_js
skill_nosql
skill_numpy
skill_pandas
skill_php
skill_power_bi
skill_python
skill_pytorch
skill_qa_testing
skill_rabbitmq
skill_react
skill_react_native
skill_redis
skill_redshift
skill_rest_api
skill_robotics
skill_ruby
skill_rust
skill_scala
skill_scikit_learn
skill_security
skill_serverless
skill_snowflake
skill_spark
skill_spring
skill_sql
skill_statistics
skill_swift
skill_tableau
skill_tensorflow
skill_terraform
skill_typescript
skill_unity
skill_vue
```

## Input rules and transformations

### India

- Request `normalized_role`, `city_grouped`, `work_mode`, `experience_midpoint_years`, `experience_range_years`, `selected_skills` map to six raw fields. Numeric experience is bounded by Pydantic (midpoint 0–35, range 0–15), then service clamps midpoint to 0–30 and range to 0–15. Unknown role/city/work-mode fall back to `Other Technology`/`Other`/`Hybrid` in service.
- Skills are normalized to `skill_*`; indicators are 0/1. Unknown values have no matching feature; duplicate selection count behavior is set-based in India.
- `ColumnTransformer` is the saved preprocessor; training code uses one-hot encoding for categorical fields and scaling for numeric fields. `handle_unknown=ignore` appears in `src/india/modeling.py`. Exact fitted details live in binary artifact and training source; M0 did not deserialize it.
- Salary service applies `expm1` to log-prediction, floors output at INR 100,000, and displays LPA (`INR / 100,000`). Target is described as salary midpoint INR in metadata.

### USA

- Request: role, seniority, city, remote boolean, list of skills. Seniority aliases are normalized; unknown seniority maps to `Mid / Unspecified`. Unknown city and role map to `Other`/`Other Tech`.
- Metadata transformer one-hot encodes the three categorical fields; `is_remote` is numeric 0/1 and `num_skills` is the length of selected input list. Skill indicators are 0/1 in metadata order. USA count uses raw selected-list length, not deduplicated matched count.
- No missing-value imputer/scaler is in the live USA metadata transformer source. Out-of-range salaries are floored at USD 30,000; output is described as annual base USD. No FX conversion is used in current comparison.

## Shared, derived, market-specific fields

- Shared concepts: occupation/role family, location, experience/seniority, skills, remote/work mode, observed/predicted salary, market aggregates.
- Market-specific names and representations: India `normalized_role`, `experience_midpoint_years`, `experience_range_years`, `city_grouped`, `work_mode`; USA `role_family`, categorical `seniority`, `city_clean`, `is_remote`, `num_skills`.
- Derived: per-market one-hot categories; skill indicators; India salary log inverse/output LPA; USA metadata one-hot plus skill vector. Cross-market mapping is currently heuristic/business grouping in `MarketService`, not a versioned canonical taxonomy.
- Allowed categories and feature order are preserved in the source files cited above; the full order is emitted in this document to make the contract inspectable.

## Leakage and validation limits

USA reports describe fold-safe preprocessing/PCA/KMeans validation; India metadata/report files describe a separate modeling workflow. Static reports are evidence of documented methodology, not an independent reproduction. M0 has not re-run training, inspected private row-level cohorts, or established absence of leakage. See `reports/leakage_audit.md`, `reports/india_preprocessing.md`, `reports/phase5_salary_prediction_report.md`.

Contract tests: `test_usa_feature_count_exact_123`, `test_india_feature_count_exact_290`, and market isolation passed. These tests prove metadata/contract assertions, not parity for every possible user profile.

## Allowed values and edge semantics confirmed from services

### India

- `normalized_role`: `AI / ML Engineer`, `Business Analyst`, `Cloud / DevOps`, `Cybersecurity`, `Data Analyst`, `Data Engineer`, `Data Scientist`, `Database Administrator`, `Frontend Developer`, `Full Stack Developer`, `Other Technology`, `Product / Program Manager`, `QA / Testing`, `Software Engineer`. Unknowns fall back to `Other Technology`.
- `city_grouped`: `Ahmedabad`, `Aurangabad`, `Bengaluru`, `Chandigarh`, `Chennai`, `Coimbatore`, `Delhi NCR`, `Faridabad`, `Gurugram`, `Hyderabad`, `Jaipur`, `Kochi`, `Kolkata`, `Mohali`, `Mumbai`, `Nagpur`, `Nashik`, `Noida`, `Other`, `Pune`, `Remote`, `Surat`, `Vadodara`. Unknowns fall back to `Other`.
- `work_mode`: `Hybrid`, `Onsite`, `Remote`; unknowns fall back to `Hybrid`.
- Pydantic permits midpoint 0–35 and range 0–15; service clamps midpoint to 0–30 and range to 0–15. `selected_skills` length ≤60; matched skill count is based on recognized feature identifiers, not raw list length.
- Currency is INR, user-facing unit is Lakhs Per Annum; model target is `log1p(salary_midpoint_inr)`, inverse transform uses `expm1`, then a ₹100,000 floor.

### USA

- `role_family`: `Backend Developer`, `Data / BI Analyst`, `Data Engineer`, `Data Scientist`, `DevOps / Cloud / Platform`, `Embedded & Hardware`, `Engineering Management`, `Frontend Developer`, `Full-Stack Developer`, `ML / AI Engineer`, `Mobile Engineer`, `Other Tech`, `QA / SDET`, `Security Engineer`, `Software Engineer`, `Solutions & Architecture`, `Systems & Network Engineer`, `Technical Product & PM`. Unknowns fall back to `Other Tech`.
- `seniority` request may use `Intern`, `Junior / Entry`, `Mid / Unspecified`, `Senior`, `Lead / Principal / Executive`, or aliases (`Entry-level`, `Mid-level`, `Lead / Principal`, `Executive / Director`). Unknowns normalize to `Mid / Unspecified`.
- `city_clean`: `Boston`, `Chicago`, `Costa Mesa`, `Denver`, `Hawthorne`, `Long Beach`, `Los Angeles`, `Mountain View`, `New York`, `New York City`, `Other`, `San Francisco`, `San Jose`, `Seattle`, `Toronto`, `Washington`. The presence of `Toronto` in a USA option set is source evidence and should be reviewed in M1; no inference is made about why it is present.
- `selected_skills` length ≤60, but `num_skills` is the raw selected list length while skill feature matching ignores unrecognized skills. This means unsupported values can affect a metadata input without activating skill indicators; contract tests should cover it before widening skill sources.
- Currency is USD, described as annual base salary; model output is floored at USD 30,000. No model-side target inverse transform appears in `USAService`.

Source: `src/backend/services/india_service.py`, `usa_service.py`, router request schemas, and the feature metadata files cited above. These are actual service categories, not a normative global taxonomy.
