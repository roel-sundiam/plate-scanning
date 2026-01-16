const Plate = require('../models/Plate');
const moment = require('moment');
const fs = require('fs').promises;
const path = require('path');

// Create new plate detection
exports.createPlate = async (req, res) => {
  try {
    const { plateNumber, gateId, confidence, image, timestamp } = req.body;
    
    // Validate required fields
    if (!plateNumber || !gateId) {
      return res.status(400).json({
        success: false,
        message: 'Plate number and gate ID are required'
      });
    }
    
    // Check for duplicates
    const duplicateWindow = parseInt(process.env.DUPLICATE_WINDOW) || 60;
    const isDuplicate = await Plate.isDuplicate(plateNumber, gateId, duplicateWindow);
    
    if (isDuplicate) {
      return res.status(200).json({
        success: true,
        message: 'Duplicate plate detected within time window',
        duplicate: true
      });
    }
    
    // Handle image storage
    let imageUrl = null;
    if (image) {
      try {
        // Decode base64 image
        const imageBuffer = Buffer.from(image, 'base64');
        const imageName = `${plateNumber}_${Date.now()}.jpg`;
        const imagePath = path.join(process.env.IMAGE_STORAGE_PATH || './uploads', imageName);
        
        // Ensure directory exists
        await fs.mkdir(path.dirname(imagePath), { recursive: true });
        
        // Save image
        await fs.writeFile(imagePath, imageBuffer);
        imageUrl = `/uploads/${imageName}`;
      } catch (imageError) {
        console.error('Error saving image:', imageError);
      }
    }
    
    // Create plate record
    const plate = new Plate({
      plateNumber: plateNumber.toUpperCase(),
      gateId,
      confidence: confidence || 0,
      timestamp: timestamp ? new Date(timestamp) : new Date(),
      imageUrl
    });
    
    await plate.save();
    
    res.status(201).json({
      success: true,
      message: 'Plate detected and saved',
      data: plate
    });
    
  } catch (error) {
    console.error('Error creating plate:', error);
    res.status(500).json({
      success: false,
      message: 'Error saving plate detection',
      error: error.message
    });
  }
};

// Get all plates with pagination and filtering
exports.getPlates = async (req, res) => {
  try {
    const {
      page = 1,
      limit = 50,
      gateId,
      plateNumber,
      startDate,
      endDate,
      verified
    } = req.query;
    
    // Build filter
    const filter = {};
    
    if (gateId) {
      filter.gateId = gateId;
    }
    
    if (plateNumber) {
      filter.$or = [
        { plateNumber: new RegExp(plateNumber, 'i') },
        { correctedPlateNumber: new RegExp(plateNumber, 'i') }
      ];
    }
    
    if (startDate || endDate) {
      filter.timestamp = {};
      if (startDate) filter.timestamp.$gte = new Date(startDate);
      if (endDate) filter.timestamp.$lte = new Date(endDate);
    }
    
    if (verified !== undefined) {
      filter.verified = verified === 'true';
    }
    
    // Execute query with pagination
    const skip = (parseInt(page) - 1) * parseInt(limit);
    const plates = await Plate.find(filter)
      .sort({ timestamp: -1 })
      .skip(skip)
      .limit(parseInt(limit));
    
    const total = await Plate.countDocuments(filter);
    
    res.json({
      success: true,
      data: plates,
      pagination: {
        total,
        page: parseInt(page),
        limit: parseInt(limit),
        pages: Math.ceil(total / parseInt(limit))
      }
    });
    
  } catch (error) {
    console.error('Error fetching plates:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching plates',
      error: error.message
    });
  }
};

// Get single plate by ID
exports.getPlateById = async (req, res) => {
  try {
    const plate = await Plate.findById(req.params.id);
    
    if (!plate) {
      return res.status(404).json({
        success: false,
        message: 'Plate not found'
      });
    }
    
    res.json({
      success: true,
      data: plate
    });
    
  } catch (error) {
    console.error('Error fetching plate:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching plate',
      error: error.message
    });
  }
};

// Search plates by plate number
exports.searchPlates = async (req, res) => {
  try {
    const { plateNumber } = req.params;
    const { limit = 20 } = req.query;
    
    const plates = await Plate.find({
      $or: [
        { plateNumber: new RegExp(plateNumber, 'i') },
        { correctedPlateNumber: new RegExp(plateNumber, 'i') }
      ]
    })
    .sort({ timestamp: -1 })
    .limit(parseInt(limit));
    
    res.json({
      success: true,
      count: plates.length,
      data: plates
    });
    
  } catch (error) {
    console.error('Error searching plates:', error);
    res.status(500).json({
      success: false,
      message: 'Error searching plates',
      error: error.message
    });
  }
};

// Update plate (for manual correction)
exports.updatePlate = async (req, res) => {
  try {
    const { correctedPlateNumber, verified, notes } = req.body;
    
    const updateData = {};
    if (correctedPlateNumber) updateData.correctedPlateNumber = correctedPlateNumber.toUpperCase();
    if (verified !== undefined) updateData.verified = verified;
    if (notes !== undefined) updateData.notes = notes;
    
    const plate = await Plate.findByIdAndUpdate(
      req.params.id,
      updateData,
      { new: true }
    );
    
    if (!plate) {
      return res.status(404).json({
        success: false,
        message: 'Plate not found'
      });
    }
    
    res.json({
      success: true,
      message: 'Plate updated successfully',
      data: plate
    });
    
  } catch (error) {
    console.error('Error updating plate:', error);
    res.status(500).json({
      success: false,
      message: 'Error updating plate',
      error: error.message
    });
  }
};

// Delete plate
exports.deletePlate = async (req, res) => {
  try {
    const plate = await Plate.findByIdAndDelete(req.params.id);
    
    if (!plate) {
      return res.status(404).json({
        success: false,
        message: 'Plate not found'
      });
    }
    
    // Delete associated image
    if (plate.imageUrl) {
      try {
        const imagePath = path.join(__dirname, '../..', plate.imageUrl);
        await fs.unlink(imagePath);
      } catch (err) {
        console.error('Error deleting image:', err);
      }
    }
    
    res.json({
      success: true,
      message: 'Plate deleted successfully'
    });
    
  } catch (error) {
    console.error('Error deleting plate:', error);
    res.status(500).json({
      success: false,
      message: 'Error deleting plate',
      error: error.message
    });
  }
};

// Get statistics
exports.getStatistics = async (req, res) => {
  try {
    const { gateId, startDate, endDate } = req.query;
    
    const stats = await Plate.getStats(gateId, startDate, endDate);
    
    // Get recent detections
    const recentPlates = await Plate.find()
      .sort({ timestamp: -1 })
      .limit(10)
      .select('plateNumber gateId timestamp confidence');
    
    // Get top plates
    const topPlates = await Plate.aggregate([
      {
        $group: {
          _id: '$plateNumber',
          count: { $sum: 1 },
          lastSeen: { $max: '$timestamp' }
        }
      },
      { $sort: { count: -1 } },
      { $limit: 10 }
    ]);
    
    res.json({
      success: true,
      data: {
        summary: stats,
        recentPlates,
        topPlates
      }
    });
    
  } catch (error) {
    console.error('Error fetching statistics:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching statistics',
      error: error.message
    });
  }
};
