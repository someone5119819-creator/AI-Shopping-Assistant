import { Modal, Box, Typography, IconButton, Button, Divider } from '@mui/material';
import { Close } from '@mui/icons-material';

export default function CartModal({ open, onClose, cartItems, cartCount, onClear }) {
    return (
        <Modal open={open} onClose={onClose}>
            <Box sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: { xs: '90%', sm: 400 },
                bgcolor: 'background.paper',
                borderRadius: 2,
                boxShadow: 24,
                p: 3
            }}>
                {/* Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" fontWeight="bold">
                        Cart ({cartCount})
                    </Typography>
                    <IconButton onClick={onClose} size="small">
                        <Close />
                    </IconButton>
                </Box>

                <Divider sx={{ mb: 2 }} />

                {/* Items */}
                {cartItems.length === 0 ? (
                    <Typography color="text.secondary" textAlign="center" py={3}>
                        Your cart is empty
                    </Typography>
                ) : (
                    <Box sx={{ maxHeight: 400, overflow: 'auto', mb: 2 }}>
                        {cartItems.map((item, idx) => (
                            <Box key={idx} sx={{ display: 'flex', gap: 2, mb: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
                                <Box
                                    component="img"
                                    src={item.image}
                                    alt={item.title}
                                    sx={{ width: 60, height: 60, objectFit: 'cover', borderRadius: 1 }}
                                />
                                <Box>
                                    <Typography variant="body2" fontWeight="500">
                                        {item.title}
                                    </Typography>
                                </Box>
                            </Box>
                        ))}
                    </Box>
                )}

                {/* Actions */}
                {cartItems.length > 0 && (
                    <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                        <Button variant="outlined" fullWidth onClick={onClear}>
                            Clear Cart
                        </Button>
                        <Button variant="contained" fullWidth onClick={onClose}>
                            Close
                        </Button>
                    </Box>
                )}
            </Box>
        </Modal>
    );
}
