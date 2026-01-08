import { Box } from '@mui/material';
import CartReview from './CartReview';
import AddressForm from './AddressForm';
import PaymentReview from './PaymentReview';
import OrderSuccess from './OrderSuccess';

export default function InlineCheckout({ stage, cartItems, onNext, onComplete, onCancel }) {
    return (
        <Box sx={{
            width: '100%',
            maxWidth: 600,
            mx: 'auto',
            p: 2
        }}>
            {stage === 'review' && (
                <CartReview
                    cartItems={cartItems}
                    onNext={() => onNext('address')}
                    onCancel={onCancel}
                />
            )}

            {stage === 'address' && (
                <AddressForm
                    onNext={(addressData) => onNext('payment', addressData)}
                    onBack={() => onNext('review')}
                />
            )}

            {stage === 'payment' && (
                <PaymentReview
                    cartItems={cartItems}
                    onPlaceOrder={onComplete}
                    onBack={() => onNext('address')}
                />
            )}

            {stage === 'success' && (
                <OrderSuccess
                    orderNumber={`DEMO-${Date.now()}`}
                    onContinue={onCancel}
                />
            )}
        </Box>
    );
}
