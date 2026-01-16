const mongoose = require('mongoose');

const plateSchema = new mongoose.Schema({
  plateNumber: {
    type: String,
    required: true,
    uppercase: true,
    trim: true,
    index: true
  },
  gateId: {
    type: String,
    required: true,
    index: true
  },
  confidence: {
    type: Number,
    min: 0,
    max: 1,
    default: 0
  },
  timestamp: {
    type: Date,
    default: Date.now,
    index: true
  },
  image: {
    type: String, // Base64 encoded or file path
    default: null
  },
  imageUrl: {
    type: String,
    default: null
  },
  verified: {
    type: Boolean,
    default: false
  },
  correctedPlateNumber: {
    type: String,
    uppercase: true,
    trim: true,
    default: null
  },
  notes: {
    type: String,
    default: null
  },
  metadata: {
    type: Map,
    of: String,
    default: {}
  }
}, {
  timestamps: true
});

// Indexes for better query performance
plateSchema.index({ plateNumber: 1, timestamp: -1 });
plateSchema.index({ gateId: 1, timestamp: -1 });

// Virtual for getting the final plate number (corrected or original)
plateSchema.virtual('finalPlateNumber').get(function() {
  return this.correctedPlateNumber || this.plateNumber;
});

// Method to check if this is a duplicate within a time window
plateSchema.statics.isDuplicate = async function(plateNumber, gateId, windowSeconds = 60) {
  const cutoffTime = new Date(Date.now() - windowSeconds * 1000);
  
  const existing = await this.findOne({
    $or: [
      { plateNumber: plateNumber },
      { correctedPlateNumber: plateNumber }
    ],
    gateId: gateId,
    timestamp: { $gte: cutoffTime }
  });
  
  return existing !== null;
};

// Method to get statistics
plateSchema.statics.getStats = async function(gateId = null, startDate = null, endDate = null) {
  const match = {};
  
  if (gateId) {
    match.gateId = gateId;
  }
  
  if (startDate || endDate) {
    match.timestamp = {};
    if (startDate) match.timestamp.$gte = new Date(startDate);
    if (endDate) match.timestamp.$lte = new Date(endDate);
  }
  
  const stats = await this.aggregate([
    { $match: match },
    {
      $group: {
        _id: null,
        totalDetections: { $sum: 1 },
        uniquePlates: { $addToSet: '$plateNumber' },
        avgConfidence: { $avg: '$confidence' },
        verifiedCount: {
          $sum: { $cond: ['$verified', 1, 0] }
        }
      }
    },
    {
      $project: {
        _id: 0,
        totalDetections: 1,
        uniquePlatesCount: { $size: '$uniquePlates' },
        avgConfidence: 1,
        verifiedCount: 1
      }
    }
  ]);
  
  return stats[0] || {
    totalDetections: 0,
    uniquePlatesCount: 0,
    avgConfidence: 0,
    verifiedCount: 0
  };
};

module.exports = mongoose.model('Plate', plateSchema);
