#!/usr/bin/env python3
"""
Calculate total subscribers from Prometheus metrics data for n8n integration.
Implements: sum(increase(godgpt_payment_success_total{exported_job="Aevatar.godgptprod.Silo"}[30d]))

Usage in n8n:
  - HTTP Request node fetches Prometheus data
  - Code node (Python) or Execute Command node runs this script
  - Input: JSON from stdin
  - Output: JSON to stdout
"""

import json
import sys
from collections import defaultdict


def calculate_increase(values: list) -> int:
    """
    Calculate increase for a counter metric.
    increase = last_value - first_value
    For Prometheus counters, this gives the total increment over the period.
    """
    if not values:
        return 0
    if len(values) == 1:
        # Single point: the value itself is the increase (counter started from 0)
        return int(values[0][1])
    
    first_value = int(values[0][1])
    last_value = int(values[-1][1])
    return last_value - first_value


def calculate_total_subscribers(data: list) -> dict:
    """
    Calculate total subscribers from Prometheus data.
    Returns breakdown by platform, purchase_type, and product.
    """
    stats = {
        "total_increase": 0,
        "by_platform": defaultdict(int),
        "by_purchase_type": defaultdict(int),
        "by_product": defaultdict(int),
    }
    
    for item in data:
        if item.get("status") != "success":
            continue
            
        results = item.get("data", {}).get("result", [])
        
        for result in results:
            metric = result.get("metric", {})
            values = result.get("values", [])
            
            platform = metric.get("payment_platform", "unknown")
            purchase_type = metric.get("purchase_type", "unknown")
            product_id = metric.get("product_id", "unknown")
            
            increase = calculate_increase(values)
            
            stats["total_increase"] += increase
            stats["by_platform"][platform] += increase
            stats["by_purchase_type"][purchase_type] += increase
            stats["by_product"][product_id] += increase
    
    # Convert defaultdicts to regular dicts for JSON serialization
    return {
        "total_increase": stats["total_increase"],
        "by_platform": dict(stats["by_platform"]),
        "by_purchase_type": dict(stats["by_purchase_type"]),
        "by_product": dict(stats["by_product"]),
    }


def main():
    """Main entry point - reads JSON from stdin, outputs JSON to stdout."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Handle both single object and array input
        if isinstance(input_data, dict):
            input_data = [input_data]
        
        # Calculate statistics
        result = calculate_total_subscribers(input_data)
        
        # Output JSON result
        print(json.dumps(result, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
