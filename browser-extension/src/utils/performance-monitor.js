// PrismWeave Performance Monitor
// Tracks extension performance and provides optimization insights

class PerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.isEnabled = true;
  }

  startTimer(operation) {
    if (!this.isEnabled) return null;
    
    const startTime = performance.now();
    const timerId = `${operation}_${Date.now()}`;
    
    this.metrics.set(timerId, {
      operation,
      startTime,
      endTime: null,
      duration: null,
      metadata: {}
    });
    
    return timerId;
  }

  endTimer(timerId, metadata = {}) {
    if (!this.isEnabled || !timerId) return null;
    
    const metric = this.metrics.get(timerId);
    if (!metric) return null;
    
    const endTime = performance.now();
    const duration = endTime - metric.startTime;
    
    metric.endTime = endTime;
    metric.duration = duration;
    metric.metadata = metadata;
    
    this.logPerformance(metric);
    return metric;
  }

  logPerformance(metric) {
    const { operation, duration, metadata } = metric;
    
    // Log slow operations
    if (duration > 1000) {
      console.warn(`🐌 Slow operation detected: ${operation} took ${duration.toFixed(2)}ms`, metadata);
    } else if (duration > 500) {
      console.info(`⚠️ Moderate operation: ${operation} took ${duration.toFixed(2)}ms`, metadata);
    } else {
      console.debug(`✅ Fast operation: ${operation} took ${duration.toFixed(2)}ms`, metadata);
    }
  }

  measureMemory() {
    if (!performance.memory) return null;
    
    return {
      used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024 * 100) / 100,
      total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024 * 100) / 100,
      limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024 * 100) / 100
    };
  }

  getMetricsSummary() {
    const operations = {};
    
    for (const [timerId, metric] of this.metrics) {
      if (!metric.duration) continue;
      
      if (!operations[metric.operation]) {
        operations[metric.operation] = {
          count: 0,
          totalDuration: 0,
          averageDuration: 0,
          minDuration: Infinity,
          maxDuration: 0
        };
      }
      
      const op = operations[metric.operation];
      op.count++;
      op.totalDuration += metric.duration;
      op.minDuration = Math.min(op.minDuration, metric.duration);
      op.maxDuration = Math.max(op.maxDuration, metric.duration);
      op.averageDuration = op.totalDuration / op.count;
    }
    
    return {
      operations,
      memory: this.measureMemory(),
      totalMetrics: this.metrics.size
    };
  }

  clearMetrics() {
    this.metrics.clear();
  }

  disable() {
    this.isEnabled = false;
  }

  enable() {
    this.isEnabled = true;
  }
}

// Create global instance
const perfMonitor = new PerformanceMonitor();

// Export for different contexts
if (typeof window !== 'undefined') {
  window.PrismWeavePerf = perfMonitor;
} else if (typeof self !== 'undefined') {
  self.PrismWeavePerf = perfMonitor;
}
