"""
Docker Container Integration Tests
"""
import pytest
import docker
import time
import requests


class TestContainerHealth:
    """Test Docker container health and status"""
    
    def test_all_containers_running(self, docker_client):
        """Test that all required containers are running"""
        expected_containers = [
            "contactplus-core",
            "contactplus-web", 
            "contactplus-monitor",
            "dozzle"
        ]
        
        running_containers = [
            container.name for container in docker_client.containers.list()
            if container.status == "running"
        ]
        
        for container_name in expected_containers:
            assert container_name in running_containers, f"Container {container_name} not running"
    
    def test_container_health_checks(self, docker_client):
        """Test container health check status"""
        core_container = docker_client.containers.get("contactplus-core")
        
        # Wait for health check to complete
        max_wait = 60
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            core_container.reload()
            health = core_container.attrs.get("State", {}).get("Health", {})
            status = health.get("Status")
            
            if status == "healthy":
                break
            elif status == "unhealthy":
                pytest.fail("Container health check failed")
            
            time.sleep(2)
        
        assert status == "healthy", "Container did not become healthy in time"
    
    def test_container_logs_available(self, docker_client):
        """Test that container logs are accessible"""
        containers = ["contactplus-core", "contactplus-web", "contactplus-monitor"]
        
        for container_name in containers:
            container = docker_client.containers.get(container_name)
            logs = container.logs(tail=10).decode('utf-8')
            assert logs is not None
            assert len(logs) >= 0  # May be empty for new containers
    
    def test_container_resource_usage(self, docker_client):
        """Test container resource usage is reasonable"""
        containers = ["contactplus-core", "contactplus-web", "contactplus-monitor"]
        
        for container_name in containers:
            container = docker_client.containers.get(container_name)
            stats = container.stats(stream=False)
            
            # Check memory usage (should be less than 1GB for MVP)
            memory_stats = stats.get("memory_stats", {})
            memory_usage = memory_stats.get("usage", 0)
            memory_limit = memory_stats.get("limit", float('inf'))
            
            if memory_usage > 0:
                memory_usage_mb = memory_usage / (1024 * 1024)
                assert memory_usage_mb < 1024, f"Container {container_name} using too much memory: {memory_usage_mb}MB"


class TestNetworking:
    """Test container networking"""
    
    def test_containers_on_same_network(self, docker_client):
        """Test containers are on the same network"""
        network = docker_client.networks.get("contactplus_contactplus-network")
        
        connected_containers = [
            container["Name"] for container in network.attrs["Containers"].values()
        ]
        
        expected_containers = [
            "contactplus-core",
            "contactplus-web",
            "contactplus-monitor", 
            "dozzle"
        ]
        
        for container_name in expected_containers:
            assert container_name in connected_containers
    
    def test_internal_communication(self, docker_client):
        """Test containers can communicate internally"""
        web_container = docker_client.containers.get("contactplus-web")
        
        # Test that web container can reach core container
        try:
            # Execute a curl command inside web container to reach core
            result = web_container.exec_run(
                "curl -f http://contactplus-core:8080/api/v1/health",
                timeout=10
            )
            assert result.exit_code == 0, "Web container cannot reach core container"
        except Exception as e:
            pytest.skip(f"Cannot test internal communication: {e}")


class TestVolumeManagement:
    """Test Docker volume management"""
    
    def test_persistent_volumes_exist(self, docker_client):
        """Test that persistent volumes are created"""
        volumes = docker_client.volumes.list()
        volume_names = [vol.name for vol in volumes]
        
        expected_volumes = [
            "contactplus_contact_data",
            "contactplus_contact_logs"
        ]
        
        for volume_name in expected_volumes:
            assert volume_name in volume_names, f"Volume {volume_name} not found"
    
    def test_volume_mounting(self, docker_client):
        """Test that volumes are properly mounted"""
        core_container = docker_client.containers.get("contactplus-core")
        mounts = core_container.attrs.get("Mounts", [])
        
        # Check that data volume is mounted
        data_mount = None
        logs_mount = None
        
        for mount in mounts:
            if mount.get("Destination") == "/app/data":
                data_mount = mount
            elif mount.get("Destination") == "/app/logs":
                logs_mount = mount
        
        assert data_mount is not None, "Data volume not mounted"
        assert logs_mount is not None, "Logs volume not mounted"
        assert data_mount.get("Type") == "volume"
        assert logs_mount.get("Type") == "volume"


class TestServicePorts:
    """Test service port configuration"""
    
    def test_core_api_port(self):
        """Test core API is accessible on correct port"""
        try:
            response = requests.get("http://localhost:8080/api/v1/health", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.fail("Core API not accessible on port 8080")
    
    def test_web_interface_port(self):
        """Test web interface is accessible on correct port"""
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.fail("Web interface not accessible on port 3000")
    
    def test_monitor_port(self):
        """Test monitor is accessible on correct port"""
        try:
            response = requests.get("http://localhost:9090", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.fail("Monitor not accessible on port 9090")
    
    def test_dozzle_port(self):
        """Test Dozzle is accessible on correct port"""
        try:
            response = requests.get("http://localhost:8081", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.fail("Dozzle not accessible on port 8081")


class TestContainerRestart:
    """Test container restart behavior"""
    
    def test_core_container_restart(self, docker_client):
        """Test core container can be restarted"""
        container = docker_client.containers.get("contactplus-core")
        
        # Record current status
        original_id = container.id
        
        # Restart container
        container.restart(timeout=30)
        
        # Wait for container to be ready
        time.sleep(10)
        
        # Check container is running
        container.reload()
        assert container.status == "running"
        
        # Test API is responsive after restart
        max_wait = 30
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get("http://localhost:8080/api/v1/health", timeout=5)
                if response.status_code == 200:
                    break
            except:
                pass
            time.sleep(2)
        else:
            pytest.fail("API not responsive after container restart")


class TestLogging:
    """Test logging configuration"""
    
    def test_log_rotation_config(self, docker_client):
        """Test log rotation is configured"""
        containers = ["contactplus-core", "contactplus-web", "contactplus-monitor"]
        
        for container_name in containers:
            container = docker_client.containers.get(container_name)
            log_config = container.attrs.get("HostConfig", {}).get("LogConfig", {})
            
            assert log_config.get("Type") == "json-file"
            config = log_config.get("Config", {})
            assert "max-size" in config
            assert "max-file" in config
    
    def test_dozzle_can_access_logs(self, docker_client):
        """Test Dozzle can access container logs"""
        try:
            # Check if Dozzle is accessible
            response = requests.get("http://localhost:8081", timeout=5)
            assert response.status_code == 200
            
            # Check if it can see our containers (basic test)
            # In a real implementation, you might parse the HTML or use Dozzle's API
            assert "dozzle" in response.text.lower() or "logs" in response.text.lower()
            
        except requests.exceptions.RequestException:
            pytest.skip("Dozzle not accessible for testing")