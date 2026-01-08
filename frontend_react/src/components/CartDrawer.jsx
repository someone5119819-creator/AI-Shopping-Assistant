import { Drawer, Box, Typography, IconButton, Button, Divider } from '@mui/material';
import { Close, Add, Remove, Delete } from '@mui/icons-material';

export default function CartDrawer({ open, onClose, cartItems, cartCount, updateCartItem, removeFromCart, onCheckout }) {
    const calculateSubtotal = () => {
        return cartItems.reduce((total, item) => {
            // Remove commas and convert to number
            const price = parseFloat(item.price.replace(/,/g, ''));
            return total + (price * item.quantity);
        }, 0);
    };

    const formatPrice = (priceStr) => {
        return priceStr.includes(',') ? priceStr : parseFloat(priceStr).toLocaleString('en-IN');
    };

    return (
        <Drawer
            anchor="right"
            open={open}
            onClose={onClose}
            sx={{
                '& .MuiDrawer-paper': {
                    width: { xs: '100%', sm: 400 },
                    p: 2
                }
            }}
        >
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5" fontWeight="bold">
                    Shopping Cart ({cartCount})
                </Typography>
                <IconButton onClick={onClose}>
                    <Close />
                </IconButton>
            </Box>

            <Divider sx={{ mb: 2 }} />

            {/* Cart Items */}
            {cartItems.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body1" color="text.secondary">
                        Your cart is empty
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Add some products to get started
                    </Typography>
                </Box>
            ) : (
                <Box sx={{ flex: 1, overflow: 'auto', mb: 2 }}>
                    {cartItems.map((item) => (
                        <Box
                            key={item.variant_id}
                            sx={{
                                display: 'flex',
                                gap: 2,
                                mb: 2,
                                p: 1.5,
                                bgcolor: 'background.paper',
                                borderRadius: 1,
                                border: '1px solid',
                                borderColor: 'divider'
                            }}
                        >
                            {/* Product Image */}
                            <Box
                                component="img"
                                src={item.image}
                                alt={item.title}
                                sx={{
                                    width: 80,
                                    height: 80,
                                    objectFit: 'cover',
                                    borderRadius: 1
                                }}
                            />

                            {/* Product Info */}
                            <Box sx={{ flex: 1 }}>
                                <Typography variant="body2" fontWeight="500" sx={{ mb: 0.5 }}>
                                    {item.title}
                                </Typography>
                                <Typography variant="h6" color="primary" fontWeight="bold">
                                    ₹{formatPrice(item.price)}
                                </Typography>

                                {/* Quantity Controls */}
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                                    <IconButton
                                        size="small"
                                        onClick={() => updateCartItem(item.variant_id, Math.max(1, item.quantity - 1))}
                                        sx={{ bgcolor: 'action.hover' }}
                                    >
                                        <Remove fontSize="small" />
                                    </IconButton>
                                    <Typography variant="body2" fontWeight="500" sx={{ minWidth: 20, textAlign: 'center' }}>
                                        {item.quantity}
                                    </Typography>
                                    <IconButton
                                        size="small"
                                        onClick={() => updateCartItem(item.variant_id, item.quantity + 1)}
                                        sx={{ bgcolor: 'action.hover' }}
                                    >
                                        <Add fontSize="small" />
                                    </IconButton>
                                    <IconButton
                                        size="small"
                                        onClick={() => removeFromCart(item.variant_id)}
                                        sx={{ ml: 'auto', color: 'error.main' }}
                                    >
                                        <Delete fontSize="small" />
                                    </IconButton>
                                </Box>
                            </Box>
                        </Box>
                    ))}
                </Box>
            )}

            {/* Footer */}
            {cartItems.length > 0 && (
                <>
                    <Divider sx={{ mb: 2 }} />
                    <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body1" fontWeight="500">
                                Subtotal:
                            </Typography>
                            <Typography variant="h6" fontWeight="bold" color="primary">
                                ₹{calculateSubtotal().toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </Typography>
                        </Box>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                            variant="outlined"
                            onClick={onClose}
                            fullWidth
                        >
                            Continue Shopping
                        </Button>
                        <Button
                            variant="contained"
                            onClick={onCheckout}
                            fullWidth
                        >
                            Checkout
                        </Button>
                    </Box>
                </>
            )}
        </Drawer>
    );
}
