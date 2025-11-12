# Troubleshooting DHRUVA-103 Error

## Problem
The `list_services` endpoint is returning:
```json
{
  "detail": {
    "kind": "DHRUVA-103",
    "message": "Request failed. Please try again."
  }
}
```

## Root Cause
DHRUVA-103 error occurs when `service_repository.find_all()` fails. This happens when **ANY** service document in MongoDB doesn't match the Service Pydantic schema. The endpoint tries to parse ALL services, and if even one is invalid, the entire operation fails.

## Diagnosis Steps

### Step 1: Run the Diagnostic Script
Run the MongoDB diagnostic script to identify problematic services:

```bash
# In MongoDB shell or MongoDB Compass
mongo < diagnose-service-issues.js
```

Or copy and paste the contents of `diagnose-service-issues.js` into MongoDB shell.

### Step 2: Run Python Validation Test (Alternative)
If you have Python access to the server:

```bash
cd Dhruva-Platform-2
python test_service_validation.py
```

This will test each service document and show which ones are invalid.

### Step 3: Check Common Issues

The most common validation failures are:

1. **Missing required fields:**
   - `api_key` (must be a string, can be empty "")
   - `endpoint` (must be a string)
   - `serviceId`, `name`, `serviceDescription`, `hardwareDescription`, `publishedOn`, `modelId`

2. **Wrong field types:**
   - `publishedOn` must be an integer (not string)
   - `api_key` must be a string
   - `healthStatus` must be `null` or an object with `status` and `lastUpdated` fields
   - `benchmarks` must be `null` or a proper dictionary structure

3. **Invalid nested structures:**
   - If `healthStatus` is provided, it must have `status: str` and `lastUpdated: str`
   - If `benchmarks` is provided, it must be `Dict[str, List[_Benchmark]]` where each benchmark has:
     - `output_length: int`
     - `generated: int`
     - `actual: int`
     - `throughput: int`
     - `50%: float`
     - `99%: float`
     - `language: str`

## Fix Steps

### Option 1: Fix Using MongoDB Scripts

1. **Fix the service document:**
   ```bash
   mongo < fix-service-document.js
   ```

2. **Fix the model document:**
   ```bash
   mongo < fix-model-document.js
   ```

### Option 2: Manual Fix in MongoDB

1. **Find the problematic service:**
   ```javascript
   db.service.find().forEach(function(service) {
     print(service.serviceId);
   });
   ```

2. **Check each service's structure:**
   ```javascript
   var service = db.service.findOne({"serviceId": "YOUR_SERVICE_ID"});
   printjson(service);
   ```

3. **Fix or delete invalid services:**
   ```javascript
   // Delete a specific invalid service
   db.service.deleteOne({"serviceId": "INVALID_SERVICE_ID"});
   
   // Or update it to fix issues
   db.service.updateOne(
     {"serviceId": "YOUR_SERVICE_ID"},
     {
       "$set": {
         "api_key": "",  // Add missing field
         "publishedOn": 0  // Fix type if needed
       },
       "$unset": {
         "invalidField": ""  // Remove invalid fields
       }
     }
   );
   ```

### Option 3: Fix All Services at Once

If you want to ensure all services have the required `api_key` field:

```javascript
// Add api_key to services that don't have it
db.service.updateMany(
  {"api_key": {"$exists": false}},
  {"$set": {"api_key": ""}}
);

// Fix publishedOn if it's stored as string
db.service.find({"publishedOn": {"$type": "string"}}).forEach(function(service) {
  db.service.updateOne(
    {"_id": service._id},
    {"$set": {"publishedOn": parseInt(service.publishedOn) || 0}}
  );
});
```

## Verification

After fixing, verify the fix:

1. **Test the endpoint:**
   ```bash
   curl -X GET "http://your-server:8000/services/details/list_services" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **Or run the validation script again:**
   ```bash
   python test_service_validation.py
   ```

## Expected Service Document Structure

```json
{
  "serviceId": "string",
  "name": "string",
  "serviceDescription": "string",
  "hardwareDescription": "string",
  "publishedOn": 0,
  "modelId": "string",
  "endpoint": "string",
  "api_key": "",
  "healthStatus": null,
  "benchmarks": null
}
```

## Expected Model Document Structure

See `indicxlit-documents-corrected.json` for the complete structure.

## Still Having Issues?

If the error persists after fixing all service documents:

1. Check server logs for the full traceback
2. Verify MongoDB connection is working
3. Check if there are any other collections or documents interfering
4. Ensure the Model documents referenced by services are also valid

