# 📡 API Documentation

This document describes the REST API endpoints available in the Hospital CRM System.

## Table of Contents

1. [Authentication](#authentication)
2. [Base URL and Headers](#base-url-and-headers)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [Patients API](#patients-api)
6. [Appointments API](#appointments-api)
7. [Billing API](#billing-api)
8. [Users API](#users-api)
9. [Dashboard API](#dashboard-api)
10. [Search API](#search-api)
11. [Health Check API](#health-check-api)

## Authentication

The API uses session-based authentication. Users must log in through the web interface before making API calls.

### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

### Logout
```http
GET /auth/logout
```

## Base URL and Headers

**Base URL**: `http://your-domain.com/api`

**Required Headers**:
```http
Content-Type: application/json
X-Requested-With: XMLHttpRequest
```

## Response Format

All API responses follow a consistent JSON format:

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    // Additional error details
  }
}
```

### Paginated Response
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `NOT_FOUND` | Resource not found |
| `PERMISSION_DENIED` | Insufficient permissions |
| `RATE_LIMITED` | Too many requests |
| `INVALID_INPUT` | Invalid input data |

## Patients API

### List Patients
```http
GET /api/patients
```

**Query Parameters**:
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20, max: 100)
- `search` (string): Search term for name, email, or phone
- `sort` (string): Sort field (name, created_at, updated_at)
- `order` (string): Sort order (asc, desc)

**Response**:
```json
{
  "patients": [
    {
      "id": 1,
      "patient_id": "P001",
      "full_name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "date_of_birth": "1990-01-01",
      "gender": "Male",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 50,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

### Get Patient Details
```http
GET /api/patients/{id}
```

**Response**:
```json
{
  "id": 1,
  "patient_id": "P001",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01",
  "gender": "Male",
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "pincode": "10001",
  "emergency_contact": "+1234567891",
  "medical_history": "No known allergies",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "recent_visits": [
    {
      "id": 1,
      "appointment_date": "2024-01-15",
      "doctor": "Dr. Smith",
      "diagnosis": "Regular checkup"
    }
  ],
  "upcoming_appointments": [
    {
      "id": 2,
      "appointment_date": "2024-02-01",
      "appointment_time": "10:00",
      "doctor": "Dr. Smith"
    }
  ]
}
```

### Create Patient
```http
POST /api/patients
Content-Type: application/json

{
  "patient_id": "P002",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "phone": "+1234567892",
  "date_of_birth": "1985-05-15",
  "gender": "Female",
  "address": "456 Oak Ave",
  "city": "Los Angeles",
  "state": "CA",
  "pincode": "90210"
}
```

### Update Patient
```http
PUT /api/patients/{id}
Content-Type: application/json

{
  "phone": "+1234567893",
  "address": "789 Pine St",
  "medical_history": "Updated medical history"
}
```

## Appointments API

### List Appointments
```http
GET /api/appointments
```

**Query Parameters**:
- `page` (int): Page number
- `per_page` (int): Items per page
- `date` (string): Filter by date (YYYY-MM-DD)
- `doctor_id` (int): Filter by doctor
- `patient_id` (int): Filter by patient
- `status` (string): Filter by status (pending, confirmed, completed, cancelled)
- `visit_type` (string): Filter by visit type (clinic, home, online)

**Response**:
```json
{
  "appointments": [
    {
      "id": 1,
      "patient": {
        "id": 1,
        "full_name": "John Doe",
        "phone": "+1234567890"
      },
      "doctor": {
        "id": 1,
        "full_name": "Dr. Smith",
        "specialization": "Physiotherapy"
      },
      "appointment_date": "2024-01-15",
      "appointment_time": "10:00",
      "visit_type": "clinic",
      "status": "confirmed",
      "reason": "Regular checkup",
      "duration_minutes": 30,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {...}
}
```

### Get Appointment Details
```http
GET /api/appointments/{id}
```

### Create Appointment
```http
POST /api/appointments
Content-Type: application/json

{
  "patient_id": 1,
  "doctor_id": 1,
  "appointment_date": "2024-02-01",
  "appointment_time": "14:30",
  "visit_type": "clinic",
  "reason": "Follow-up consultation",
  "duration_minutes": 45,
  "notes": "Patient requested afternoon slot"
}
```

### Update Appointment Status
```http
PUT /api/appointments/{id}/status
Content-Type: application/json

{
  "status": "confirmed",
  "notes": "Appointment confirmed by patient"
}
```

### Cancel Appointment
```http
DELETE /api/appointments/{id}
Content-Type: application/json

{
  "reason": "Patient requested cancellation"
}
```

## Billing API

### List Bills
```http
GET /api/billing
```

**Query Parameters**:
- `page` (int): Page number
- `per_page` (int): Items per page
- `patient_id` (int): Filter by patient
- `status` (string): Filter by payment status (pending, partial, paid, overdue)
- `date_from` (string): Start date filter (YYYY-MM-DD)
- `date_to` (string): End date filter (YYYY-MM-DD)

### Get Bill Details
```http
GET /api/billing/{id}
```

### Create Bill
```http
POST /api/billing
Content-Type: application/json

{
  "patient_id": 1,
  "bill_number": "B001",
  "total_amount": 150.00,
  "description": "Physiotherapy session",
  "due_date": "2024-02-15",
  "items": [
    {
      "description": "Consultation",
      "quantity": 1,
      "unit_price": 100.00,
      "total": 100.00
    },
    {
      "description": "Therapy session",
      "quantity": 1,
      "unit_price": 50.00,
      "total": 50.00
    }
  ]
}
```

### Record Payment
```http
POST /api/billing/{id}/payment
Content-Type: application/json

{
  "amount": 150.00,
  "payment_method": "card",
  "transaction_id": "TXN123456",
  "notes": "Full payment received"
}
```

## Users API

### List Users
```http
GET /api/users
```

**Query Parameters**:
- `page` (int): Page number
- `per_page` (int): Items per page
- `role` (string): Filter by role (super_admin, admin, doctor, staff, patient)
- `active` (boolean): Filter by active status

### Get User Details
```http
GET /api/users/{id}
```

### Create User
```http
POST /api/users
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "first_name": "New",
  "last_name": "User",
  "role": "staff",
  "phone": "+1234567894",
  "password": "securepassword123"
}
```

### Update User
```http
PUT /api/users/{id}
Content-Type: application/json

{
  "email": "updated@example.com",
  "phone": "+1234567895",
  "is_active": true
}
```

## Dashboard API

### Get Dashboard Statistics
```http
GET /api/dashboard/stats
```

**Response**:
```json
{
  "patients": {
    "total": 150,
    "new_this_month": 12,
    "active": 140
  },
  "appointments": {
    "today": 8,
    "this_week": 45,
    "pending": 15,
    "confirmed": 25
  },
  "billing": {
    "total_revenue": 15000.00,
    "pending_payments": 2500.00,
    "this_month_revenue": 3500.00
  },
  "system": {
    "users": 25,
    "active_sessions": 8
  }
}
```

### Get Recent Activities
```http
GET /api/dashboard/activities
```

## Search API

### Global Search
```http
GET /api/search?q={query}
```

**Query Parameters**:
- `q` (string): Search query (minimum 3 characters)
- `type` (string): Filter by type (patients, appointments, users)
- `limit` (int): Maximum results (default: 10, max: 50)

**Response**:
```json
{
  "results": [
    {
      "type": "patient",
      "id": 1,
      "title": "John Doe",
      "subtitle": "Patient ID: P001",
      "url": "/patients/1",
      "highlight": "john@example.com"
    },
    {
      "type": "appointment",
      "id": 1,
      "title": "Appointment with Dr. Smith",
      "subtitle": "2024-01-15 10:00",
      "url": "/appointments/1",
      "highlight": "Regular checkup"
    }
  ],
  "total": 2,
  "query": "john"
}
```

## Health Check API

### Application Health
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "environment": "production",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 15.2
    },
    "redis": {
      "status": "healthy",
      "response_time_ms": 2.1
    },
    "disk_space": {
      "status": "healthy",
      "used_percent": 45.2,
      "free_gb": 25.8
    }
  }
}
```

### Detailed Health Check
```http
GET /api/health/detailed
```

## Rate Limiting

API endpoints are rate limited to prevent abuse:

- **General endpoints**: 100 requests per 15 minutes per IP
- **Authentication endpoints**: 10 requests per 15 minutes per IP
- **Search endpoints**: 50 requests per 15 minutes per IP

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Examples

### JavaScript/Fetch
```javascript
// Get patients
const response = await fetch('/api/patients', {
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
});
const data = await response.json();

// Create appointment
const appointment = await fetch('/api/appointments', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  body: JSON.stringify({
    patient_id: 1,
    doctor_id: 1,
    appointment_date: '2024-02-01',
    appointment_time: '14:30',
    visit_type: 'clinic',
    reason: 'Follow-up'
  })
});
```

### Python/Requests
```python
import requests

# Login first
session = requests.Session()
session.post('http://localhost:5000/auth/login', data={
    'username': 'admin',
    'password': 'password'
})

# Get patients
response = session.get('http://localhost:5000/api/patients')
patients = response.json()

# Create appointment
appointment_data = {
    'patient_id': 1,
    'doctor_id': 1,
    'appointment_date': '2024-02-01',
    'appointment_time': '14:30',
    'visit_type': 'clinic',
    'reason': 'Follow-up'
}
response = session.post('http://localhost:5000/api/appointments', 
                       json=appointment_data)
```

### cURL
```bash
# Login and save cookies
curl -c cookies.txt -X POST http://localhost:5000/auth/login \
  -d "username=admin&password=password"

# Get patients
curl -b cookies.txt http://localhost:5000/api/patients

# Create appointment
curl -b cookies.txt -X POST http://localhost:5000/api/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "doctor_id": 1,
    "appointment_date": "2024-02-01",
    "appointment_time": "14:30",
    "visit_type": "clinic",
    "reason": "Follow-up"
  }'
```
