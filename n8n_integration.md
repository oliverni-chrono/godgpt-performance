# n8n Integration Guide for Prometheus Payment Metrics

## Overview

This script calculates `sum(increase(godgpt_payment_success_total[30d]))` from Prometheus query results.

## n8n Workflow Setup

### Option 1: Execute Command Node (Recommended)

```
[HTTP Request] → [Execute Command] → [Set/Transform]
```

**HTTP Request Node:**
- Method: GET
- URL: Your Prometheus endpoint
- Query: `godgpt_payment_success_total{exported_job="Aevatar.godgptprod.Silo"}`

**Execute Command Node:**
```
echo '{{ JSON.stringify($input.all()[0].json) }}' | python3 /path/to/calculate_subscribers.py
```

### Option 2: Code Node (JavaScript Equivalent)

If you prefer native n8n JavaScript, use this in a Code node:

```javascript
// n8n Code Node - JavaScript version
const items = $input.all();

function calculateIncrease(values) {
  if (!values || values.length === 0) return 0;
  if (values.length === 1) return parseInt(values[0][1]);
  return parseInt(values[values.length - 1][1]) - parseInt(values[0][1]);
}

let totalIncrease = 0;
const byPlatform = {};
const byPurchaseType = {};
const byProduct = {};

for (const item of items) {
  const data = item.json;
  if (data.status !== 'success') continue;
  
  const results = data.data?.result || [];
  
  for (const result of results) {
    const metric = result.metric || {};
    const values = result.values || [];
    
    const platform = metric.payment_platform || 'unknown';
    const purchaseType = metric.purchase_type || 'unknown';
    const productId = metric.product_id || 'unknown';
    
    const increase = calculateIncrease(values);
    
    totalIncrease += increase;
    byPlatform[platform] = (byPlatform[platform] || 0) + increase;
    byPurchaseType[purchaseType] = (byPurchaseType[purchaseType] || 0) + increase;
    byProduct[productId] = (byProduct[productId] || 0) + increase;
  }
}

return [{
  json: {
    total_increase: totalIncrease,
    by_platform: byPlatform,
    by_purchase_type: byPurchaseType,
    by_product: byProduct
  }
}];
```

## Output Format

```json
{
  "total_increase": 123,
  "by_platform": {
    "AppStore": 85,
    "GooglePlay": 20,
    "Stripe": 18
  },
  "by_purchase_type": {
    "Renewal": 90,
    "Subscription": 33
  },
  "by_product": {
    "weekly6": 70,
    "monthly20": 30,
    "...": "..."
  }
}
```

## Python Script Usage

```bash
# From stdin
cat prometheus_response.json | python3 calculate_subscribers.py

# Or with curl directly
curl -s "http://prometheus:9090/api/v1/query_range?..." | python3 calculate_subscribers.py
```









