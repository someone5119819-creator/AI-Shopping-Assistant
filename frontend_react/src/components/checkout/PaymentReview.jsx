import { Box, Typography, Button, Divider, Card, CardContent, Radio, RadioGroup, FormControlLabel } from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import { useState } from 'react';

export default function PaymentReview({ cartItems, onPlaceOrder, onBack }) {
    const [paymentMethod, setPaymentMethod] = useState('cod');

    const calculateSubtotal = () => {
        return cartItems.reduce((sum, item) => {
            const price = parseFloat(item.price.replace(/[,₹]/g, ''));
            return sum + price;
        }, 0);
    };

    const subtotal = calculateSubtotal();
    const tax = subtotal * 0.18;
    const delivery = 50;
    const total = subtotal + tax + delivery;

    return (
        <Box>
            {/* Header */}
            <Typography variant="h5" fontWeight="bold" sx={{ mb: 3 }}>
                Review & Payment
            </Typography>

            {/* Items Summary */}
            <Typography variant="subtitle1" fontWeight="600" sx={{ mb: 2 }}>
                Order Items ({cartItems.length})
            </Typography>
            <Box sx={{ mb: 3 }}>
                {cartItems.map((item, idx) => (
                    <Card key={idx} elevation={0} sx={{
                        mb: 1.5,
                        background: 'rgba(240, 253, 250, 0.5)',
                        border: '1px solid rgba(167, 243, 208, 0.2)',
                        borderRadius: 1.5
                    }}>
                        <CardContent sx={{ display: 'flex', gap: 2, p: 1.5, '&:last-child': { pb: 1.5 } }}>
                            <Box
                                component="img"
                                src={item.image}
                                alt={item.title}
                                sx={{ width: 60, height: 60, objectFit: 'cover', borderRadius: 1 }}
                            />
                            <Box sx={{ flex: 1 }}>
                                <Typography variant="body2" fontWeight="600">
                                    {item.title}
                                </Typography>
                                <Typography variant="body2" color="#059669" fontWeight="bold">
                                    ₹{item.price}
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                ))}
            </Box>

            {/* Payment Method (Demo) */}
            <Typography variant="subtitle1" fontWeight="600" sx={{ mb: 2 }}>
                Payment Method
            </Typography>
            <Box sx={{
                bgcolor: 'rgba(240, 253, 250, 0.5)',
                p: 2,
                borderRadius: 2,
                mb: 3
            }}>
                <RadioGroup value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)}>
                    <FormControlLabel value="cod" control={<Radio />} label="Cash on Delivery (Demo)" />
                    <FormControlLabel value="online" control={<Radio />} label="Online Payment (Demo)" disabled />
                </RadioGroup>
            </Box>

            {/* Price Summary */}
            <Box sx={{ bgcolor: 'rgba(240, 253, 250, 0.7)', p: 2, borderRadius: 2, mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>Subtotal:</Typography>
                    <Typography>₹{subtotal.toLocaleString('en-IN')}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>Tax (GST 18%):</Typography>
                    <Typography>₹{tax.toLocaleString('en-IN')}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>Delivery:</Typography>
                    <Typography>₹{delivery}</Typography>
                </Box>
                <Divider sx={{ my: 1.5 }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="h6" fontWeight="bold">Grand Total:</Typography>
                    <Typography variant="h6" fontWeight="bold" color="#059669">
                        ₹{total.toLocaleString('en-IN')}
                    </Typography>
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
                    variant="contained"
                    fullWidth
                    onClick={() => onPlaceOrder({ total, subtotal, tax, delivery })}
                    sx={{
                        bgcolor: '#059669',
                        py: 1.5,
                        '&:hover': { bgcolor: '#047857' }
                    }}
                >
                    Place Order - ₹{total.toLocaleString('en-IN')}
                </Button>
            </Box>
        </Box>
    );
}
