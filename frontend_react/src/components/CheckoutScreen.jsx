import { Modal, Box, Typography, Button, Divider, IconButton } from '@mui/material';
import { Close } from '@mui/icons-material';

export default function CheckoutScreen({ open, onClose, cartItems, onPlaceOrder }) {
    const calculateSubtotal = () => {
        return cartItems.reduce((sum, item) => {
            const price = parseFloat(item.price.replace(/[,₹]/g, ''));
            return sum + (price * item.quantity);
        }, 0);
    };

    const subtotal = calculateSubtotal();
    const tax = subtotal * 0.18; // 18% GST
    const delivery = 50;
    const total = subtotal + tax + delivery;

    return (
        <Modal open={open} onClose={onClose}>
            <Box sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: { xs: '95%', sm: '90%', md: 800 },
                maxHeight: '90vh',
                bgcolor: 'background.paper',
                borderRadius: 3,
                boxShadow: 24,
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column'
            }}>
                {/* Header */}
                <Box sx={{ p: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center', bgcolor: 'primary.main', color: 'white' }}>
                    <Typography variant="h5" fontWeight="bold">
                        Checkout
                    </Typography>
                    <IconButton onClick={onClose} sx={{ color: 'white' }}>
                        <Close />
                    </IconButton>
                </Box>

                {/* Content */}
                <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                        Order Summary
                    </Typography>

                    {/* Items List */}
                    {cartItems.map((item, idx) => (
                        <Box key={idx} sx={{
                            display: 'flex',
                            gap: 2,
                            mb: 2,
                            p: 2,
                            bgcolor: 'grey.50',
                            borderRadius: 2
                        }}>
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
                                <Typography variant="body2" color="text.secondary">
                                    Qty: {item.quantity}
                                </Typography>
                                <Typography variant="h6" color="primary" fontWeight="bold" sx={{ mt: 0.5 }}>
                                    ₹{parseFloat(item.price.replace(/[,₹]/g, '')).toLocaleString('en-IN')}
                                </Typography>
                            </Box>
                        </Box>
                    ))}

                    <Divider sx={{ my: 3 }} />

                    {/* Price Breakdown */}
                    <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography>Subtotal:</Typography>
                            <Typography>₹{subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography>Tax (GST 18%):</Typography>
                            <Typography>₹{tax.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography>Delivery:</Typography>
                            <Typography>₹{delivery.toLocaleString('en-IN')}</Typography>
                        </Box>
                        <Divider sx={{ my: 2 }} />
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="h6" fontWeight="bold">Total:</Typography>
                            <Typography variant="h6" fontWeight="bold" color="primary">
                                ₹{total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                            </Typography>
                        </Box>
                    </Box>
                </Box>

                {/* Footer */}
                <Box sx={{ p: 3, bgcolor: 'grey.50', borderTop: '1px solid', borderColor: 'divider' }}>
                    <Button
                        variant="contained"
                        fullWidth
                        size="large"
                        onClick={() => onPlaceOrder({ subtotal, tax, delivery, total })}
                        sx={{ py: 1.5 }}
                    >
                        Place Order - ₹{total.toLocaleString('en-IN')}
                    </Button>
                </Box>
            </Box>
        </Modal>
    );
}
