const express = require('express');
const router = express.Router();
const plateController = require('../controllers/plateController');

// Create new plate detection
router.post('/', plateController.createPlate);

// Get all plates with filtering and pagination
router.get('/', plateController.getPlates);

// Get statistics
router.get('/statistics', plateController.getStatistics);

// Search plates by plate number
router.get('/search/:plateNumber', plateController.searchPlates);

// Get single plate by ID
router.get('/:id', plateController.getPlateById);

// Update plate (manual correction)
router.put('/:id', plateController.updatePlate);

// Delete plate
router.delete('/:id', plateController.deletePlate);

module.exports = router;
