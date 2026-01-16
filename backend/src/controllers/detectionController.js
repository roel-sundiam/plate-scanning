const { spawn } = require('child_process');
const path = require('path');

let detectionProcess = null;
let detectionStatus = 'stopped'; // stopped, starting, running, stopping

// Start detection service
exports.startDetection = async (req, res) => {
  try {
    if (detectionProcess) {
      return res.status(400).json({
        success: false,
        message: 'Detection service is already running'
      });
    }

    const { source = 'iphone', device = '1' } = req.body;
    const pythonPath = path.join(__dirname, '../../../python-service');
    
    detectionStatus = 'starting';
    
    // Spawn Python process using test_real_plate.py with API integration
    detectionProcess = spawn('python', ['test_real_plate.py', device], {
      cwd: pythonPath,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    let output = '';
    
    detectionProcess.stdout.on('data', (data) => {
      output += data.toString();
      console.log(`Detection: ${data}`);
    });

    detectionProcess.stderr.on('data', (data) => {
      console.error(`Detection Error: ${data}`);
    });

    detectionProcess.on('close', (code) => {
      console.log(`Detection process exited with code ${code}`);
      detectionProcess = null;
      detectionStatus = 'stopped';
    });

    detectionProcess.on('error', (error) => {
      console.error(`Failed to start detection: ${error.message}`);
      detectionProcess = null;
      detectionStatus = 'stopped';
    });

    // Wait a bit to see if it starts successfully
    await new Promise(resolve => setTimeout(resolve, 2000));

    if (detectionProcess) {
      detectionStatus = 'running';
      res.json({
        success: true,
        message: `Detection service started with source: ${source}`,
        status: detectionStatus
      });
    } else {
      detectionStatus = 'stopped';
      res.status(500).json({
        success: false,
        message: 'Failed to start detection service',
        error: output
      });
    }

  } catch (error) {
    detectionStatus = 'stopped';
    console.error('Error starting detection:', error);
    res.status(500).json({
      success: false,
      message: 'Error starting detection service',
      error: error.message
    });
  }
};

// Stop detection service
exports.stopDetection = async (req, res) => {
  try {
    if (!detectionProcess) {
      return res.status(400).json({
        success: false,
        message: 'Detection service is not running'
      });
    }

    detectionStatus = 'stopping';
    
    // Try graceful shutdown first
    detectionProcess.stdin.write('q\n');
    
    // Force kill after 3 seconds if still running
    setTimeout(() => {
      if (detectionProcess) {
        detectionProcess.kill('SIGTERM');
        setTimeout(() => {
          if (detectionProcess) {
            detectionProcess.kill('SIGKILL');
          }
        }, 1000);
      }
    }, 3000);

    detectionProcess = null;
    detectionStatus = 'stopped';

    res.json({
      success: true,
      message: 'Detection service stopped',
      status: detectionStatus
    });

  } catch (error) {
    console.error('Error stopping detection:', error);
    res.status(500).json({
      success: false,
      message: 'Error stopping detection service',
      error: error.message
    });
  }
};

// Get detection status
exports.getStatus = async (req, res) => {
  try {
    res.json({
      success: true,
      status: detectionStatus,
      isRunning: detectionProcess !== null,
      pid: detectionProcess ? detectionProcess.pid : null
    });
  } catch (error) {
    console.error('Error getting status:', error);
    res.status(500).json({
      success: false,
      message: 'Error getting detection status',
      error: error.message
    });
  }
};
