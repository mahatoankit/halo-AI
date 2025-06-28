/**
 * Real-time IoT Sensor Data Client
 * Provides JavaScript functions for continuous sensor data updates
 */

class RealtimeIoTClient {
    constructor(baseUrl = '/sensors/api/enhanced') {
        this.baseUrl = baseUrl;
        this.pollingInterval = null;
        this.updateCallback = null;
        this.errorCallback = null;
        this.isPolling = false;
        this.pollInterval = 5000; // 5 seconds default
    }

    /**
     * Start real-time polling for sensor data
     * @param {string} sensorId - Sensor ID to monitor
     * @param {function} onUpdate - Callback for data updates
     * @param {function} onError - Callback for errors
     * @param {number} intervalMs - Polling interval in milliseconds (default: 5000)
     */
    startRealTimeUpdates(sensorId = 'bhairahawa_farm_1', onUpdate, onError, intervalMs = 5000) {
        this.stopRealTimeUpdates(); // Stop any existing polling
        
        this.updateCallback = onUpdate;
        this.errorCallback = onError;
        this.pollInterval = intervalMs;
        this.isPolling = true;

        console.log(`🔴 Starting real-time updates for sensor: ${sensorId}`);
        console.log(`📡 Polling interval: ${intervalMs}ms`);

        // Initial fetch
        this.fetchLiveData(sensorId);

        // Start polling
        this.pollingInterval = setInterval(() => {
            if (this.isPolling) {
                this.fetchLiveData(sensorId);
            }
        }, intervalMs);
    }

    /**
     * Stop real-time polling
     */
    stopRealTimeUpdates() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        this.isPolling = false;
        console.log('⏹️ Stopped real-time updates');
    }

    /**
     * Fetch live sensor data (bypasses cache)
     * @param {string} sensorId - Sensor ID
     */
    async fetchLiveData(sensorId) {
        try {
            const response = await fetch(`${this.baseUrl}/live/?sensor_id=${sensorId}`);
            const data = await response.json();

            if (data.status === 'success' && data.data) {
                const sensorReading = data.data.reading;
                console.log(`📊 Live data for ${sensorId}:`, sensorReading);
                
                if (this.updateCallback) {
                    this.updateCallback(sensorReading, data.data);
                }
            } else {
                throw new Error(data.message || 'Failed to fetch live data');
            }
        } catch (error) {
            console.error(`❌ Error fetching live data for ${sensorId}:`, error);
            if (this.errorCallback) {
                this.errorCallback(error);
            }
        }
    }

    /**
     * Fetch continuous stream data with diagnostics
     * @param {string} sensorId - Sensor ID
     * @param {boolean} includeDiagnostics - Include health diagnostics
     */
    async fetchStreamData(sensorId, includeDiagnostics = false) {
        try {
            const url = `${this.baseUrl}/stream/?sensor_id=${sensorId}&diagnostics=${includeDiagnostics}`;
            const response = await fetch(url);
            const data = await response.json();

            if (data.status === 'success') {
                return data.data;
            } else {
                throw new Error(data.message || 'Failed to fetch stream data');
            }
        } catch (error) {
            console.error(`❌ Error fetching stream data:`, error);
            throw error;
        }
    }

    /**
     * Get all sensors data with optional real-time refresh
     * @param {boolean} useCache - Whether to use cached data
     */
    async getAllSensorsData(useCache = false) {
        try {
            const response = await fetch(`${this.baseUrl}/sensors/all/?use_cache=${useCache}`);
            const data = await response.json();
            return data.data;
        } catch (error) {
            console.error('❌ Error fetching all sensors data:', error);
            throw error;
        }
    }

    /**
     * Update DOM elements with sensor data
     * @param {object} sensorData - Sensor reading data
     */
    updateDOMElements(sensorData) {
        // Update temperature
        const tempElement = document.getElementById('sensor-temperature');
        if (tempElement) {
            tempElement.textContent = `${sensorData.temperature}°C`;
        }

        // Update pH
        const phElement = document.getElementById('sensor-ph');
        if (phElement) {
            phElement.textContent = sensorData.ph;
        }

        // Update humidity
        const humidityElement = document.getElementById('sensor-humidity');
        if (humidityElement) {
            humidityElement.textContent = `${sensorData.humidity}%`;
        }

        // Update soil temperature
        const soilTempElement = document.getElementById('sensor-soil-temperature');
        if (soilTempElement) {
            soilTempElement.textContent = `${sensorData.soil_temperature}°C`;
        }

        // Update timestamp
        const timestampElement = document.getElementById('sensor-timestamp');
        if (timestampElement) {
            const date = new Date(sensorData.timestamp);
            timestampElement.textContent = date.toLocaleString();
        }

        // Update status indicator
        const statusElement = document.getElementById('sensor-status');
        if (statusElement) {
            statusElement.textContent = sensorData.status;
            statusElement.className = `status-${sensorData.status}`;
        }
    }

    /**
     * Create a visual dashboard update
     * @param {object} sensorData - Sensor reading data
     * @param {object} metadata - Additional metadata
     */
    updateDashboard(sensorData, metadata) {
        // Update DOM elements
        this.updateDOMElements(sensorData);

        // Trigger custom event for other components
        const event = new CustomEvent('sensorDataUpdate', {
            detail: { sensorData, metadata }
        });
        document.dispatchEvent(event);

        // Visual feedback for real-time updates
        const indicator = document.getElementById('realtime-indicator');
        if (indicator) {
            indicator.classList.add('active');
            setTimeout(() => indicator.classList.remove('active'), 1000);
        }
    }
}

// Create global instance
const realtimeIoT = new RealtimeIoTClient();

// Example usage functions
function startSensorMonitoring(sensorId = 'bhairahawa_farm_1') {
    realtimeIoT.startRealTimeUpdates(
        sensorId,
        (sensorData, metadata) => {
            console.log('📊 Sensor update:', sensorData);
            realtimeIoT.updateDashboard(sensorData, metadata);
        },
        (error) => {
            console.error('❌ Sensor error:', error);
            // Show error notification
            showErrorNotification('Failed to fetch sensor data: ' + error.message);
        },
        3000 // Update every 3 seconds
    );
}

function stopSensorMonitoring() {
    realtimeIoT.stopRealTimeUpdates();
}

function showErrorNotification(message) {
    // Create or update error notification
    let notification = document.getElementById('sensor-error-notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'sensor-error-notification';
        notification.className = 'error-notification';
        document.body.appendChild(notification);
    }
    notification.textContent = message;
    notification.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        notification.style.display = 'none';
    }, 5000);
}

// Auto-start monitoring when page loads (optional)
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔴 Real-time IoT client ready');
    
    // Uncomment to auto-start monitoring
    // startSensorMonitoring();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RealtimeIoTClient, realtimeIoT };
}
