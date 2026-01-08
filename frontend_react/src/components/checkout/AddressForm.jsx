import { Box, Typography, Button, TextField } from '@mui/material';
import { ArrowBack, ArrowForward } from '@mui/icons-material';
import { useState } from 'react';

export default function AddressForm({ onNext, onBack }) {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        address: '',
        city: '',
        pincode: ''
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        onNext(formData);
    };

    return (
        <Box component="form" onSubmit={handleSubmit}>
            {/* Header */}
            <Typography variant="h5" fontWeight="bold" sx={{ mb: 3 }}>
                Delivery Address
            </Typography>

            {/* Form Fields */}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
                <TextField
                    label="Full Name"
                    required
                    fullWidth
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
                <TextField
                    label="Email"
                    type="email"
                    required
                    fullWidth
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
                <TextField
                    label="Phone"
                    type="tel"
                    required
                    fullWidth
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
                <TextField
                    label="Address"
                    required
                    fullWidth
                    multiline
                    rows={2}
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                />
                <Box sx={{ display: 'flex', gap: 2 }}>
                    <TextField
                        label="City"
                        required
                        fullWidth
                        value={formData.city}
                        onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    />
                    <TextField
                        label="PIN Code"
                        required
                        fullWidth
                        value={formData.pincode}
                        onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
                    />
                </Box>
            </Box>

            {/* Buttons */}
            <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<ArrowBack />}
                    onClick={onBack}
                    sx={{
                        borderColor: '#059669',
                        color: '#059669',
                        '&:hover': { borderColor: '#047857', bgcolor: 'rgba(5, 150, 105, 0.04)' }
                    }}
                >
                    Back
                </Button>
                <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    endIcon={<ArrowForward />}
                    sx={{
                        bgcolor: '#059669',
                        '&:hover': { bgcolor: '#047857' }
                    }}
                >
                    Continue
                </Button>
            </Box>
        </Box>
    );
}
