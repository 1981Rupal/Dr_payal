# tests/test_performance.py - Performance Tests

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from models import db, Patient, Appointment, User, UserRole

class TestPerformance:
    """Test application performance under various loads"""
    
    def test_patient_list_performance(self, app, authenticated_client):
        """Test patient list endpoint performance with large dataset"""
        
        # Create a large number of patients
        with app.app_context():
            patients = []
            for i in range(100):  # Create 100 patients
                patient = Patient(
                    patient_id=f'PERF{i:03d}',
                    first_name=f'Patient{i}',
                    last_name='Performance',
                    phone=f'+123456{i:04d}',
                    email=f'perf{i}@test.com'
                )
                patients.append(patient)
            
            db.session.add_all(patients)
            db.session.commit()
        
        # Measure response time
        start_time = time.time()
        response = authenticated_client.get('/api/patients')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Should respond within 2 seconds
        
        # Test pagination performance
        start_time = time.time()
        response = authenticated_client.get('/api/patients?page=1&per_page=20')
        end_time = time.time()
        
        pagination_time = end_time - start_time
        assert response.status_code == 200
        assert pagination_time < 1.0  # Pagination should be faster
    
    def test_search_performance(self, app, authenticated_client):
        """Test search performance with large dataset"""
        
        # Create patients with searchable data
        with app.app_context():
            patients = []
            for i in range(200):
                patient = Patient(
                    patient_id=f'SEARCH{i:03d}',
                    first_name=f'SearchPatient{i}',
                    last_name=f'TestLast{i}',
                    phone=f'+987654{i:04d}',
                    email=f'search{i}@test.com'
                )
                patients.append(patient)
            
            db.session.add_all(patients)
            db.session.commit()
        
        # Test search performance
        search_terms = ['SearchPatient1', 'TestLast5', '+987654']
        
        for term in search_terms:
            start_time = time.time()
            response = authenticated_client.get(f'/api/search?q={term}')
            end_time = time.time()
            
            search_time = end_time - start_time
            
            assert response.status_code == 200
            assert search_time < 1.0  # Search should be fast
    
    def test_concurrent_requests(self, authenticated_client):
        """Test handling of concurrent requests"""
        
        def make_request():
            """Make a single request"""
            response = authenticated_client.get('/api/dashboard/stats')
            return response.status_code == 200
        
        # Test with multiple concurrent requests
        num_threads = 10
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_request) for _ in range(num_threads)]
            
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        # All requests should succeed
        assert all(results)
        assert len(results) == num_threads
    
    def test_database_query_performance(self, app):
        """Test database query performance"""
        
        with app.app_context():
            # Create test data
            patients = []
            for i in range(50):
                patient = Patient(
                    patient_id=f'DBPERF{i:03d}',
                    first_name=f'DBPatient{i}',
                    last_name='Performance',
                    phone=f'+111222{i:04d}',
                    email=f'dbperf{i}@test.com'
                )
                patients.append(patient)
            
            db.session.add_all(patients)
            db.session.commit()
            
            # Test query performance
            start_time = time.time()
            
            # Complex query with joins and filters
            results = db.session.query(Patient).filter(
                Patient.first_name.like('DBPatient%')
            ).order_by(Patient.created_at.desc()).limit(20).all()
            
            end_time = time.time()
            query_time = end_time - start_time
            
            assert len(results) > 0
            assert query_time < 0.5  # Query should be fast
    
    def test_appointment_creation_performance(self, app, test_patient, test_doctor):
        """Test appointment creation performance"""
        
        with app.app_context():
            appointments = []
            start_time = time.time()
            
            # Create multiple appointments
            for i in range(20):
                appointment = Appointment(
                    patient_id=test_patient.id,
                    doctor_id=test_doctor.id,
                    appointment_date=date.today() + timedelta(days=i),
                    appointment_time=time(10, 0),
                    visit_type='clinic',
                    reason=f'Performance test appointment {i}'
                )
                appointments.append(appointment)
            
            db.session.add_all(appointments)
            db.session.commit()
            
            end_time = time.time()
            creation_time = end_time - start_time
            
            assert creation_time < 2.0  # Should create 20 appointments quickly
    
    def test_memory_usage(self, app, authenticated_client):
        """Test memory usage during operations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform memory-intensive operations
        for _ in range(10):
            response = authenticated_client.get('/api/patients')
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB for this test)
        assert memory_increase < 50

class TestLoadTesting:
    """Load testing scenarios"""
    
    def test_sustained_load(self, authenticated_client):
        """Test application under sustained load"""
        
        def sustained_requests():
            """Make sustained requests"""
            success_count = 0
            for _ in range(20):
                try:
                    response = authenticated_client.get('/health')
                    if response.status_code == 200:
                        success_count += 1
                    time.sleep(0.1)  # Small delay between requests
                except Exception:
                    pass
            return success_count
        
        # Run sustained load test
        start_time = time.time()
        success_count = sustained_requests()
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Should handle most requests successfully
        assert success_count >= 18  # Allow for some failures
        assert total_time < 10  # Should complete within reasonable time
    
    def test_burst_load(self, authenticated_client):
        """Test application under burst load"""
        
        def burst_request():
            """Single burst request"""
            try:
                response = authenticated_client.get('/health')
                return response.status_code == 200
            except Exception:
                return False
        
        # Create burst of concurrent requests
        num_requests = 20
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(burst_request) for _ in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        burst_time = end_time - start_time
        
        success_rate = sum(results) / len(results)
        
        # Should handle burst load reasonably well
        assert success_rate >= 0.8  # 80% success rate
        assert burst_time < 5  # Should complete burst quickly

class TestCaching:
    """Test caching performance"""
    
    def test_repeated_requests_performance(self, authenticated_client):
        """Test that repeated requests benefit from caching"""
        
        # First request (cache miss)
        start_time = time.time()
        response1 = authenticated_client.get('/api/dashboard/stats')
        first_request_time = time.time() - start_time
        
        assert response1.status_code == 200
        
        # Second request (should be faster due to caching)
        start_time = time.time()
        response2 = authenticated_client.get('/api/dashboard/stats')
        second_request_time = time.time() - start_time
        
        assert response2.status_code == 200
        
        # Second request should be faster (or at least not significantly slower)
        # Allow some variance due to system load
        assert second_request_time <= first_request_time * 1.5

class TestScalability:
    """Test application scalability"""
    
    def test_large_dataset_handling(self, app, authenticated_client):
        """Test handling of large datasets"""
        
        with app.app_context():
            # Create a large dataset
            patients = []
            batch_size = 100
            
            for batch in range(5):  # 5 batches of 100 = 500 patients
                batch_patients = []
                for i in range(batch_size):
                    patient_id = batch * batch_size + i
                    patient = Patient(
                        patient_id=f'SCALE{patient_id:04d}',
                        first_name=f'ScalePatient{patient_id}',
                        last_name='Scalability',
                        phone=f'+555000{patient_id:04d}',
                        email=f'scale{patient_id}@test.com'
                    )
                    batch_patients.append(patient)
                
                db.session.add_all(batch_patients)
                db.session.commit()  # Commit in batches
        
        # Test querying large dataset
        start_time = time.time()
        response = authenticated_client.get('/api/patients?per_page=50')
        query_time = time.time() - start_time
        
        assert response.status_code == 200
        assert query_time < 3.0  # Should handle large dataset reasonably
        
        # Test search on large dataset
        start_time = time.time()
        response = authenticated_client.get('/api/search?q=ScalePatient')
        search_time = time.time() - start_time
        
        assert response.status_code == 200
        assert search_time < 2.0  # Search should still be fast
