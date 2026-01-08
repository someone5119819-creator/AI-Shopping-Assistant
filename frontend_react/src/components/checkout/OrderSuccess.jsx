import { Box, Typography, Button } from '@mui/material';
import { CheckCircle, ShoppingBag } from '@mui/icons-material';
import { useEffect, useState } from 'react';

export default function OrderSuccess({ orderNumber, onContinue }) {
    const [show, setShow] = useState(false);

    useEffect(() => {
        setTimeout(() => setShow(true), 100);
    }, []);

    return (
        <Box sx={{
            textAlign: 'center',
            py: 4,
            opacity: show ? 1 : 0,
            transform: show ? 'scale(1)' : 'scale(0.9)',
            transition: 'all 0.3s ease-out'
        }}>
            {/* Animated Checkmark */}
            <Box sx={{
                width: 100,
                height: 100,
                borderRadius: '50%',
                bgcolor: '#059669',
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
                bgcolor: 'rgba(240, 253, 250, 0.7)',
                p: 3,
                borderRadius: 2,
                mb: 3,
                maxWidth: 400,
                mx: 'auto'
            }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                    Order Number
                </Typography>
                <Typography variant="h5" fontWeight="bold" color="#059669" sx={{ mb: 2 }}>
                    {orderNumber}
                </Typography>

                <Typography variant="caption" color="warning.main" display="block">
                    ⚠️ This is a DEMO - No real order was created
                </Typography>
            </Box>

            {/* Continue Button */}
            <Button
                variant="contained"
                size="large"
                startIcon={<ShoppingBag />}
                onClick={onContinue}
                sx={{
                    bgcolor: '#059669',
                    px: 4,
                    py: 1.5,
                    '&:hover': { bgcolor: '#047857' }
                }}
            >
                Continue Shopping
            </Button>
        </Box>
    );
}
