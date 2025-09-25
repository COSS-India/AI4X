# MongoDB to PostgreSQL Data Type Mapping

## Overview
This document outlines the data type conversions and mapping strategy for migrating from MongoDB to PostgreSQL in the Dhruva Platform 2 application.

## Primary Key Strategy
- **MongoDB**: `ObjectId` (12-byte identifier)
- **PostgreSQL**: `UUID` (universally unique identifier)
- **Conversion**: Each MongoDB ObjectId is mapped to a consistent UUID using a mapping table

## Field-by-Field Mapping

### Users Collection → users Table
| MongoDB Field | MongoDB Type | PostgreSQL Column | PostgreSQL Type | Notes |
|---------------|--------------|-------------------|-----------------|-------|
| `_id` | ObjectId | `id` | UUID | Primary key conversion |
| `name` | String | `name` | VARCHAR(255) | Direct mapping |
| `email` | String | `email` | VARCHAR(255) | Unique constraint |
| `password` | String | `password` | VARCHAR(255) | Hashed password |
| `role` | String | `role` | VARCHAR(50) | Enum-like constraint |

### API Key Collection → api_keys Table
| MongoDB Field | MongoDB Type | PostgreSQL Column | PostgreSQL Type | Notes |
|---------------|--------------|-------------------|-----------------|-------|
| `_id` | ObjectId | `id` | UUID | Primary key conversion |
| `name` | String | `name` | VARCHAR(255) | Direct mapping |
| `api_key` | String | `api_key` | VARCHAR(255) | Unique constraint |
| `masked_key` | String | `masked_key` | VARCHAR(255) | Direct mapping |
| `active` | Boolean | `active` | BOOLEAN | Direct mapping |
| `user_id` | ObjectId | `user_id` | UUID | Foreign key to users |
| `type` | String | `type` | VARCHAR(50) | Direct mapping |
| `created_timestamp` | Date | `created_timestamp` | TIMESTAMP WITH TIME ZONE | Direct mapping |
| `usage` | Number | `usage` | INTEGER | Direct mapping |
| `hits` | Number | `hits` | INTEGER | Direct mapping |
| `data_tracking` | Boolean | `data_tracking` | BOOLEAN | Direct mapping |
| `services` | Array | `services` | JSONB | Complex array stored as JSON |

### Model Collection → models Table
| MongoDB Field | MongoDB Type | PostgreSQL Column | PostgreSQL Type | Notes |
|---------------|--------------|-------------------|-----------------|-------|
| `_id` | ObjectId | `id` | UUID | Primary key conversion |
| `modelId` | String | `model_id` | VARCHAR(255) | Unique business key |
| `version` | String | `version` | VARCHAR(100) | Direct mapping |
| `submittedOn` | Number | `submitted_on` | BIGINT | Unix timestamp |
| `updatedOn` | Number | `updated_on` | BIGINT | Unix timestamp |
| `name` | String | `name` | VARCHAR(255) | Direct mapping |
| `description` | String | `description` | TEXT | Direct mapping |
| `refUrl` | String | `ref_url` | VARCHAR(500) | Direct mapping |
| `task` | Object | `task` | JSONB | Complex object as JSON |
| `languages` | Array | `languages` | JSONB | Array of objects as JSON |
| `license` | String | `license` | VARCHAR(255) | Direct mapping |
| `domain` | Array | `domain` | JSONB | Array of strings as JSON |
| `inferenceEndPoint` | Object | `inference_endpoint` | JSONB | Complex nested object |
| `benchmarks` | Array | `benchmarks` | JSONB | Optional array of objects |
| `submitter` | Object | `submitter` | JSONB | Complex nested object |

### Service Collection → services Table
| MongoDB Field | MongoDB Type | PostgreSQL Column | PostgreSQL Type | Notes |
|---------------|--------------|-------------------|-----------------|-------|
| `_id` | ObjectId | `id` | UUID | Primary key conversion |
| `serviceId` | String | `service_id` | VARCHAR(255) | Unique business key |
| `name` | String | `name` | VARCHAR(255) | Direct mapping |
| `serviceDescription` | String | `service_description` | TEXT | Direct mapping |
| `hardwareDescription` | String | `hardware_description` | TEXT | Direct mapping |
| `publishedOn` | Number | `published_on` | BIGINT | Unix timestamp |
| `modelId` | String | `model_id` | VARCHAR(255) | Foreign key to models |
| `endpoint` | String | `endpoint` | VARCHAR(500) | Direct mapping |
| `api_key` | String | `api_key` | VARCHAR(255) | Direct mapping |
| `healthStatus` | Object | `health_status` | JSONB | Optional complex object |
| `benchmarks` | Object | `benchmarks` | JSONB | Optional complex object |

### Session Collection → sessions Table
| MongoDB Field | MongoDB Type | PostgreSQL Column | PostgreSQL Type | Notes |
|---------------|--------------|-------------------|-----------------|-------|
| `_id` | ObjectId | `id` | UUID | Primary key conversion |
| `user_id` | ObjectId | `user_id` | UUID | Foreign key to users |
| `type` | String | `type` | VARCHAR(100) | Direct mapping |
| `timestamp` | Date | `timestamp` | TIMESTAMP WITH TIME ZONE | Direct mapping |

### Feedback Collection → feedback Table
| MongoDB Field | MongoDB Type | PostgreSQL Column | PostgreSQL Type | Notes |
|---------------|--------------|-------------------|-----------------|-------|
| `_id` | ObjectId | `id` | UUID | Primary key conversion |
| `user_id` | ObjectId | `user_id` | UUID | Foreign key to users |
| `api_key_name` | String | `api_key_name` | VARCHAR(255) | Direct mapping |
| `pipelineInput` | Object | `pipeline_input` | JSONB | Complex ULCA object |
| `pipelineOutput` | Object | `pipeline_output` | JSONB | Complex ULCA object |
| `suggestedPipelineOutput` | Object | `suggested_pipeline_output` | JSONB | Complex ULCA object |
| `pipelineFeedback` | Object | `pipeline_feedback` | JSONB | Complex ULCA object |

## Complex Object Handling

### JSONB Usage Strategy
PostgreSQL's JSONB type is used for:
1. **Arrays of Objects**: Like `services` in api_keys, `benchmarks` in models
2. **Complex Nested Objects**: Like `inferenceEndPoint`, `submitter` in models
3. **ULCA Protocol Objects**: Like feedback pipeline objects
4. **Dynamic Schemas**: Objects that may have varying structures

### Benefits of JSONB
- Maintains MongoDB document flexibility
- Supports indexing on JSON fields
- Allows complex queries on nested data
- Preserves original data structure

## Index Strategy

### Primary Indexes
- All primary keys (UUID)
- All foreign keys
- Unique business identifiers (email, api_key, model_id, service_id)

### Performance Indexes
- Frequently queried fields (name, active status)
- Timestamp fields for sorting
- GIN indexes on JSONB fields for complex queries

### JSONB Indexes
```sql
-- Example: Index on task type in models
CREATE INDEX idx_models_task_type ON models USING GIN((task->>'type'));

-- Example: Index on service usage in api_keys
CREATE INDEX idx_api_keys_services ON api_keys USING GIN(services);
```

## Migration Considerations

### Data Integrity
- Foreign key constraints ensure referential integrity
- Check constraints validate enum-like values
- NOT NULL constraints prevent missing required data

### Performance
- Indexes created for all frequently queried fields
- JSONB provides efficient storage and querying for complex objects
- Timestamp fields use timezone-aware types

### Compatibility
- All MongoDB query patterns can be replicated in PostgreSQL
- Complex aggregations can use PostgreSQL's JSON functions
- Full-text search available on text fields

## Rollback Strategy
- Original MongoDB ObjectIds are preserved in mapping table
- All conversions are reversible
- Data validation ensures no data loss during migration
