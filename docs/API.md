# PyFSD GenAI - API Documentation

## Overview

This document provides comprehensive API documentation for the PyFSD GenAI platform. The API follows RESTful principles and uses JSON for data exchange.

## Base URL

```
https://api.pyfsdgenai.com/api/v1
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## API Endpoints

### Health Check

#### GET /health
Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "service": "PyFSD GenAI",
  "version": "1.0.0",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### Contract Management

#### POST /contracts/upload
Upload a contract document for processing.

**Request Body:**
```json
{
  "filename": "contract.pdf",
  "content_type": "application/pdf",
  "file_size": 1024000,
  "document_type": "pdf",
  "contract_type": "service"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Contract uploaded successfully",
  "data": {
    "contract_id": "contract_123",
    "status": "pending",
    "uploaded_at": "2025-01-01T00:00:00Z"
  }
}
```

#### GET /contracts
Retrieve a list of contracts.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)
- `status` (optional): Filter by status
- `contract_type` (optional): Filter by contract type

**Response:**
```json
{
  "items": [
    {
      "id": "contract_123",
      "title": "Service Agreement",
      "contract_type": "service",
      "parties": ["Company A", "Company B"],
      "status": "completed",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "has_next": false,
  "has_prev": false
}
```

#### GET /contracts/{contract_id}
Retrieve a specific contract.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "contract_123",
    "title": "Service Agreement",
    "contract_type": "service",
    "parties": ["Company A", "Company B"],
    "effective_date": "2025-01-01T00:00:00Z",
    "expiration_date": "2025-12-31T23:59:59Z",
    "value": 100000.00,
    "currency": "USD",
    "status": "completed",
    "pricing_info": {
      "base_price": 100000.00,
      "discount_rate": 0.05,
      "payment_terms": "Net 30"
    },
    "terms_conditions": {
      "termination_clause": "30 days notice",
      "liability_limit": 1000000.00
    },
    "quality_score": 8.5
  }
}
```

#### POST /contracts/{contract_id}/process
Start processing a contract with AI agents.

**Response:**
```json
{
  "success": true,
  "message": "Contract processing started",
  "data": {
    "job_id": "job_456",
    "status": "processing",
    "estimated_completion": "2025-01-01T00:05:00Z"
  }
}
```

#### GET /contracts/{contract_id}/processing-status
Get the processing status of a contract.

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "job_456",
    "status": "processing",
    "progress": 75,
    "agents_completed": 15,
    "total_agents": 20,
    "estimated_completion": "2025-01-01T00:02:00Z"
  }
}
```

### Invoice Management

#### POST /invoices/upload
Upload an invoice for reconciliation.

**Request Body:**
```json
{
  "invoice_number": "INV-001",
  "vendor": "Vendor Corp",
  "amount": 5000.00,
  "currency": "USD",
  "invoice_date": "2025-01-01T00:00:00Z",
  "due_date": "2025-01-31T23:59:59Z",
  "contract_id": "contract_123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Invoice uploaded successfully",
  "data": {
    "invoice_id": "invoice_789",
    "status": "pending",
    "uploaded_at": "2025-01-01T00:00:00Z"
  }
}
```

#### GET /invoices
Retrieve a list of invoices.

**Query Parameters:**
- `page` (optional): Page number
- `page_size` (optional): Items per page
- `status` (optional): Filter by status
- `contract_id` (optional): Filter by contract

**Response:**
```json
{
  "items": [
    {
      "id": "invoice_789",
      "invoice_number": "INV-001",
      "vendor": "Vendor Corp",
      "amount": 5000.00,
      "status": "reconciled",
      "reconciled": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "has_next": false,
  "has_prev": false
}
```

#### POST /invoices/{invoice_id}/reconcile
Start invoice reconciliation process.

**Response:**
```json
{
  "success": true,
  "message": "Invoice reconciliation started",
  "data": {
    "reconciliation_id": "recon_101",
    "status": "processing",
    "estimated_completion": "2025-01-01T00:02:00Z"
  }
}
```

#### GET /invoices/{invoice_id}/reconciliation-result
Get invoice reconciliation results.

**Response:**
```json
{
  "success": true,
  "data": {
    "invoice_id": "invoice_789",
    "contract_id": "contract_123",
    "reconciled": true,
    "price_match": true,
    "terms_match": true,
    "quantity_match": true,
    "discrepancies": [],
    "confidence_score": 0.95,
    "reconciled_at": "2025-01-01T00:02:00Z"
  }
}
```

### Contract Benchmarking

#### POST /contracts/{contract_id}/benchmark
Start contract benchmarking process.

**Response:**
```json
{
  "success": true,
  "message": "Contract benchmarking started",
  "data": {
    "benchmark_id": "bench_202",
    "status": "processing",
    "estimated_completion": "2025-01-01T00:03:00Z"
  }
}
```

#### GET /contracts/{contract_id}/benchmark-result
Get contract benchmarking results.

**Response:**
```json
{
  "success": true,
  "data": {
    "contract_id": "contract_123",
    "overall_score": 8.5,
    "dimension_scores": {
      "pricing": 9.0,
      "terms": 8.0,
      "risk": 8.5,
      "compliance": 9.0
    },
    "strengths": [
      "Competitive pricing",
      "Clear payment terms",
      "Strong compliance framework"
    ],
    "weaknesses": [
      "Limited termination flexibility",
      "High liability exposure"
    ],
    "recommendations": [
      "Negotiate better termination terms",
      "Consider liability insurance"
    ],
    "industry_average": 7.2,
    "percentile_rank": 85.5,
    "generated_at": "2025-01-01T00:03:00Z"
  }
}
```

### Agent Management

#### GET /agents
Get list of available AI agents.

**Response:**
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "agent_id": "pricing_agent_1",
        "agent_name": "Pricing Structure Agent",
        "category": "pricing",
        "status": "active",
        "description": "Extracts pricing structures and rates"
      },
      {
        "agent_id": "terms_agent_1",
        "agent_name": "Terms & Conditions Agent",
        "category": "terms",
        "status": "active",
        "description": "Analyzes contractual terms and conditions"
      }
    ],
    "total_agents": 20,
    "active_agents": 20
  }
}
```

#### GET /agents/{agent_id}/status
Get status of a specific agent.

**Response:**
```json
{
  "success": true,
  "data": {
    "agent_id": "pricing_agent_1",
    "agent_name": "Pricing Structure Agent",
    "status": "idle",
    "last_processed": "2025-01-01T00:00:00Z",
    "total_processed": 150,
    "success_rate": 0.98
  }
}
```

### Reports and Analytics

#### GET /reports/contracts/summary
Get contract processing summary report.

**Query Parameters:**
- `start_date` (optional): Start date for report
- `end_date` (optional): End date for report
- `contract_type` (optional): Filter by contract type

**Response:**
```json
{
  "success": true,
  "data": {
    "total_contracts": 150,
    "processed_contracts": 145,
    "pending_contracts": 5,
    "average_processing_time": 4.2,
    "average_quality_score": 8.1,
    "contract_types": {
      "service": 80,
      "supply": 45,
      "software": 25
    },
    "processing_stats": {
      "success_rate": 0.97,
      "error_rate": 0.03
    }
  }
}
```

#### GET /reports/invoices/reconciliation-summary
Get invoice reconciliation summary report.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_invoices": 500,
    "reconciled_invoices": 480,
    "pending_reconciliation": 20,
    "discrepancies_found": 15,
    "average_confidence_score": 0.94,
    "cost_savings": 25000.00,
    "currency": "USD"
  }
}
```

## Error Responses

### Standard Error Format
```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Error Codes

- `INVALID_INPUT` - Invalid input data
- `FILE_TOO_LARGE` - File size exceeds limit
- `UNSUPPORTED_FORMAT` - Unsupported file format
- `PROCESSING_FAILED` - Document processing failed
- `AGENT_UNAVAILABLE` - AI agent not available
- `CONTRACT_NOT_FOUND` - Contract not found
- `INVOICE_NOT_FOUND` - Invoice not found
- `RECONCILIATION_FAILED` - Invoice reconciliation failed

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Standard users**: 100 requests per hour
- **Premium users**: 1000 requests per hour
- **Enterprise users**: 10000 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Webhooks

The API supports webhooks for real-time notifications:

### Webhook Events
- `contract.processing.completed`
- `contract.processing.failed`
- `invoice.reconciliation.completed`
- `invoice.reconciliation.failed`
- `contract.benchmark.completed`

### Webhook Payload Example
```json
{
  "event": "contract.processing.completed",
  "data": {
    "contract_id": "contract_123",
    "job_id": "job_456",
    "processing_time": 4.2,
    "quality_score": 8.5
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## SDKs and Libraries

### Python SDK
```bash
pip install pyfsdgenai-sdk
```

```python
from pyfsdgenai import PyFSDGenAI

client = PyFSDGenAI(api_key="your-api-key")
contract = client.contracts.upload("contract.pdf")
```

### JavaScript SDK
```bash
npm install pyfsdgenai-sdk
```

```javascript
const PyFSDGenAI = require('pyfsdgenai-sdk');
const client = new PyFSDGenAI('your-api-key');
const contract = await client.contracts.upload('contract.pdf');
```

## Support

For API support and questions:
- **Documentation**: https://docs.pyfsdgenai.com
- **Support Email**: support@pyfsdgenai.com
- **Status Page**: https://status.pyfsdgenai.com

---

**API Version**: 1.0.0  
**Last Updated**: January 2025  
**Base URL**: https://api.pyfsdgenai.com/api/v1



