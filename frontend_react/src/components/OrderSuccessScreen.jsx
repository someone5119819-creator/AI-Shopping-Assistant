import { Modal, Box, Typography, Button } from '@mui/material';
import { CheckCircle } from '@mui/icons-material';
import { useEffect, useState } from 'react';

export default function OrderSuccessScreen({ open, onClose, orderNumber, total }) {
    const [show, setShow] = useState(false);

    useEffect(() => {
        if (open) {
            setTimeout(() => setShow(true), 100);
        } else {
            setShow(false);
        }
    }, [open]);

    return (
        <Modal open={open} onClose={onClose}>
            <Box sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: show ? 'translate(-50%, -50%) scale(1)' : 'translate(-50%, -50%) scale(0.9)',
                opacity: show ? 1 : 0,
                transition: 'all 0.3s ease-out',
                width: { xs: '90%', sm: 500 },
                bgcolor: 'background.paper',
                borderRadius: 3,
                boxShadow: 24,
                p: 4,
                textAlign: 'center'
            }}>
                {/* Animated Checkmark */}
                <Box sx={{
                    width: 100,
                    height: 100,
                    borderRadius: '50%',
                    bgcolor: 'success.main',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 24px',
                    animation: show ? 'checkmarkPop 0.5s ease-out' : 'none',
                    '@keyframes checkmarkPop': {
                        '0%': { transform: 'scale(0)' },
                        '50%': { transform: 'scale(1.1)' },
                        '100%': { transform: 'scale(1)' }
                    }
                }}>
                    <CheckCircle sx={{ fontSize: 60, color: 'white' }} />
                </Box>

                {/* Success Message */}
                <Typography variant="h4" fontWeight="bold" gutterBottom>
                    Order Placed!
                </Typography>

                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                    Your order has been successfully placed.
                </Typography>

                {/* Order Details */}
                <Box sx={{
                    bgcolor: 'grey.50',
                    p: 3,
                    borderRadius: 2,
                    mb: 3
                }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                        Order Number
                    </Typography>
                    <Typography variant="h5" fontWeight="bold" color="primary" sx={{ mb: 2 }}>
                        {orderNumber}
                    </Typography>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                        Total Amount
                    </Typography>
                    <Typography variant="h6" fontWeight="bold">
                        ₹{parseFloat(total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </Typography>
                </Box>

                <Typography variant="caption" color="warning.main" display="block" sx={{ mb: 3 }}>
                    ⚠️ This is a DEMO - No real order was created
                </Typography>

                {/* Continue Button */}
                <Button
                    variant="contained"
                    fullWidth
                    size="large"
                    onClick={onClose}
                >
                    Continue Shopping
                </Button>
            </Box>
        </Modal>
    );
}
