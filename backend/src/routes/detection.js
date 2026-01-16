const express = require('express');
const router = express.Router();
const detectionController = require('../controllers/detectionController');

// Start detection service
router.post('/start', detectionController.startDetection);

// Stop detection service
router.post('/stop', detectionController.stopDetection);

// Get detection status
router.get('/status', detectionController.getStatus);

module.exports = router;
