import { Box, Typography, Button, Divider, Card, CardContent } from '@mui/material';
import { ArrowForward, Close } from '@mui/icons-material';

export default function CartReview({ cartItems, onNext, onCancel }) {
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
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h5" fontWeight="bold">
                    Cart Review
                </Typography>
                <Button
                    startIcon={<Close />}
                    onClick={onCancel}
                    sx={{ color: 'text.secondary' }}
                >
                    Cancel
                </Button>
            </Box>

            {/* Items */}
            <Box sx={{ mb: 3 }}>
                {cartItems.map((item, idx) => (
                    <Card key={idx} elevation={0} sx={{
                        mb: 2,
                        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 253, 250, 0.95) 100%)',
                        border: '1px solid rgba(167, 243, 208, 0.3)',
                        borderRadius: 2
                    }}>
                        <CardContent sx={{ display: 'flex', gap: 2, p: 2, '&:last-child': { pb: 2 } }}>
                            <Box
                                component="img"
                                src={item.image}
                                alt={item.title}
                                sx={{ width: 80, height: 80, objectFit: 'cover', borderRadius: 1 }}
                            />
                            <Box sx={{ flex: 1 }}>
                                <Typography variant="body1" fontWeight="600">
                                    {item.title}
                                </Typography>
                                <Typography variant="h6" color="#059669" fontWeight="bold" sx={{ mt: 0.5 }}>
                                    ₹{item.price}
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                ))}
            </Box>

            <Divider sx={{ my: 2 }} />

            {/* Price Summary */}
            <Box sx={{ bgcolor: 'rgba(240, 253, 250, 0.5)', p: 2, borderRadius: 2, mb: 3 }}>
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
                <Divider sx={{ my: 1 }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="h6" fontWeight="bold">Total:</Typography>
                    <Typography variant="h6" fontWeight="bold" color="#059669">
                        ₹{total.toLocaleString('en-IN')}
                    </Typography>
                </Box>
            </Box>

            {/* Next Button */}
            <Button
                variant="contained"
                fullWidth
                size="large"
                endIcon={<ArrowForward />}
                onClick={onNext}
                sx={{
                    bgcolor: '#059669',
                    py: 1.5,
                    '&:hover': { bgcolor: '#047857' }
                }}
            >
                Proceed to Address
            </Button>
        </Box>
    );
}
